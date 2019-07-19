import random
from tile import get_all_tiles, MAX_SIDE_VALUE
from dominoes_util import Dir, Orientation, opposite

class TileIndex(object):
  def __init__(self):
    self.reset()

  def reset(self):
    self.index = {side: set() for side in range(MAX_SIDE_VALUE + 1)}
    self.tiles = set()
    for tile in get_all_tiles():
      self.add_tile(tile)

  def remove_tile(self, tile):
    self.index[tile.small_side].remove(tile)
    if not tile.is_double():
      self.index[tile.big_side].remove(tile)
    self.tiles.remove(tile)

  def add_tile(self, tile):
    self.index[tile.small_side].add(tile)
    if not tile.is_double():
        self.index[tile.big_side].add(tile)
    self.tiles.add(tile)

class Board(object):
  def __init__(self):
    self.remaining_tile_index = TileIndex()
    self.reset()

  def reset(self):
    self.main_row = []
    self.up = []
    self.down = []
    self.spinner = None
    self.bone_yard = set()
    self.history = []
    self.end_sides = {Dir.LEFT: None, Dir.RIGHT: None, Dir.UP: None, Dir.DOWN: None}
    self.remaining_tile_index.reset()

  def _valid_starting_moves(self):
    return [(t, Dir.RIGHT) for t in get_all_tiles()]

  def get_valid_moves(self):
    if not self.main_row:
      return self._valid_starting_moves()
    dirs = [Dir.LEFT, Dir.RIGHT]
    if self._can_play_up_or_down():
      dirs += [Dir.UP, Dir.DOWN]
    valid_moves = []
    for direction in dirs:
      side = self.end_sides[direction]
      for tile in self.remaining_tile_index.index[side]:
        valid_moves.append((tile, direction))
    return valid_moves

  def get_tiles_on_board(self):
    return self.main_row + self.up + self.down

  def get_num_tiles_on_board(self):
    return len(self.get_tiles_on_board())

  def _update_spinner(self, tile):
    if not self.spinner and tile.is_double():
      self.spinner = tile
      side = tile.small_side
      self.end_sides[Dir.UP] = side
      self.end_sides[Dir.DOWN] = side

  def get_total_count(self):
    if not self.main_row:
      return 0
    elif len(self.main_row) == 1:
      return self.main_row[0].total_points()
    else:
      up_points = 0 if not self.up else self.up[-1].up_points()
      down_points = 0 if not self.down else self.down[-1].down_points()
      return (up_points + down_points + self.main_row[0].left_points() +
              self.main_row[-1].right_points())

  def score(self):
    total_count = self.get_total_count()
    if total_count and total_count % 5 == 0:
      return total_count
    return 0

  def _get_end_side(self, direction):
    return self.end_sides[direction]

  def end_is_double(self, direction):
    if not self.main_row:
      return False
    if direction == Dir.LEFT:
      return self.main_row[0].is_double()
    elif direction == Dir.RIGHT:
      return self.main_row[-1].is_double()
    elif direction == Dir.UP:
      if self.up:
        return self.up[-1].is_double()
    elif direction == Dir.DOWN:
      if self.down:
        return self.down[-1].is_double()
    return False

  def _orientation_big_side_in_or_out(self, direction, out):
    if direction == Dir.LEFT:
      return Orientation.BIG_LEFT if out else Orientation.BIG_RIGHT
    if direction == Dir.RIGHT:
      return Orientation.BIG_RIGHT if out else Orientation.BIG_LEFT
    if direction == Dir.UP:
      return Orientation.BIG_UP if out else Orientation.BIG_DOWN
    if direction == Dir.DOWN:
      return Orientation.BIG_DOWN if out else Orientation.BIG_UP

  def _orientation_big_side_in(self, direction):
    return self._orientation_big_side_in_or_out(direction, False)

  def _orientation_big_side_out(self, direction):
    return self._orientation_big_side_in_or_out(direction, True)

  def _get_orientation(self, tile, direction):
    if tile.is_double():
      return Orientation.DOUBLE
    elif not self.main_row:
      return Orientation.BIG_RIGHT
    elif self._get_end_side(direction) == tile.big_side:
      return self._orientation_big_side_in(direction)
    else:
      return self._orientation_big_side_out(direction)

  def _set_orientation(self, tile, direction):
    tile.orientation = self._get_orientation(tile, direction)

  def _tiles_to_moves(self, tiles, direction):
    return [(t, direction) for t in tiles]

  def _add_to_row(self, tile, direction):
    if direction == Dir.LEFT:
      self.main_row = [tile] + self.main_row
    elif direction == Dir.RIGHT:
      self.main_row.append(tile)
    elif direction == Dir.UP:
      self.up.append(tile)
    elif direction == Dir.DOWN:
      self.down.append(tile)

  def _get_tile_sides(self, tile, direction):
    if direction == Dir.LEFT:
      return tile.left_side(), tile.right_side()
    elif direction == Dir.RIGHT:
      return tile.right_side(), tile.left_side()
    elif direction == Dir.UP:
      return tile.up_side(), tile.down_side()
    elif direction == Dir.DOWN:
      return tile.down_side(), tile.up_side()

  def add_tile_to_board(self, tile, direction):
    self._set_orientation(tile, direction)
    self._add_to_row(tile, direction)
    self._update_spinner(tile)
    tile_side, opp_side = self._get_tile_sides(tile, direction)
    self.end_sides[direction] = tile_side
    self.remaining_tile_index.remove_tile(tile)
    if len(self.main_row) == 1:
      self.end_sides[opposite(direction)] = opp_side

  def _remove_tile_from_side(self, direction):
    if direction == Dir.LEFT:
      removed_tile = self.main_row[0]
      self.main_row = self.main_row[1:]
      new_end = None
      if self.main_row:
        new_end = self.main_row[0].left_side()
    elif direction == Dir.RIGHT:
      removed_tile = self.main_row[-1]
      self.main_row = self.main_row[:-1]
      new_end = None
      if self.main_row:
        new_end = self.main_row[-1].right_side()
    elif direction == Dir.UP:
      removed_tile = self.up[-1]
      self.up = self.up[:-1]
      new_end = self.spinner.small_side
      if self.up:
        new_end = self.up[-1].up_side()
    elif direction == Dir.DOWN:
      removed_tile = self.down[-1]
      self.down = self.down[:-1]
      new_end = self.spinner.small_side
      if self.down:
        new_end = self.down[-1].down_side()
    return removed_tile, new_end

  def _remove_spinner(self):
    self.spinner = None
    self.end_sides[Dir.UP] = None
    self.end_sides[Dir.DOWN] = None

  def remove_from_board(self, direction):
    tile, new_end = self._remove_tile_from_side(direction)
    self.end_sides[direction] = new_end
    if self.spinner and tile == self.spinner:
      self._remove_spinner()
    self.remaining_tile_index.add_tile(tile)
    if not self.main_row:
      self.end_sides[opposite(direction)] = None

  def _spinner_on_end(self):
    return self.spinner and self.main_row and (
        self.main_row[0] == self.spinner or self.main_row[-1] == self.spinner)

  def _can_play_up_or_down(self):
    if self.spinner and not self._spinner_on_end():
      return True
    else:
      return False

  def valid_move(self, tile, direction):
    if (direction == Dir.UP or direction == Dir.DOWN) and not self._can_play_up_or_down():
      return False
    elif not self.main_row:
      return direction == Dir.LEFT or direction == Dir.RIGHT
    else:
      return (tile.small_side == self._get_end_side(direction) or
              tile.big_side == self._get_end_side(direction))

  def make_move(self, tile, direction):
    self.add_tile_to_board(tile, direction)
    return self.score()

  def undo_move(self, tile, direction):
    if tile is None:
      return last_move
    self.remove_from_board(direction)
    tile.orientation = Orientation.NOT_ON_BOARD

  def tiles_in_bone_yard(self):
    return len(self.bone_yard) > 0

  def draw_from_bone_yard(self, player_name):
    tile = random.choice(tuple(self.bone_yard))
    self.bone_yard.remove(tile)
    return tile

  def _down_repr(self):
    if not self.down:
      return str(self.down)
    down_repr = '['
    for tile in self.down:
      down_repr += tile.switched_repr() + ', '
    return down_repr[:-2] + ']'

  def __repr__(self):
    return ('Board:\nSpinner: ' +  str(self.spinner) + '\nMain row: ' +
            str(self.main_row) + '\nUp: ' + str(self.up) + '\nDown: ' +
            self._down_repr() + '\nCount: ' + str(self.get_total_count()))
