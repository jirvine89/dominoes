import random
from dominoes_util import Dir, Orientation

class Board:
  def __init__(self):
    self.reset()

  def reset(self):
    self.main_row = []
    self.up = []
    self.down = []
    self.spinner = None
    self.bone_yard = set()
    self.total_count = 0
    self.history = []
    self.left_side = None
    self.right_side = None
    self.up_side = None
    self.down_side = None

  def get_tiles_on_board(self):
    return self.main_row + self.up + self.down

  def get_num_tiles_on_board(self):
    return len(self.get_tiles_on_board)

  def _update_spinner(self, tile):
    if not self.spinner and tile.is_double():
      self.spinner = tile
      self.up_side = tile.small_side
      self.down_side = tile.small_side

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
    if self.total_count and self.total_count % 5 == 0:
      return self.total_count
    return 0

  def _update_total_count(self):
    self.total_count = self.get_total_count()

  # TODO: test this is the same as old version
  def _get_end_side(self, direction):
    if direction == Dir.LEFT:
        return self.left_side
    elif direction == Dir.RIGHT:
        return self.right_side
    elif direction == Dir.UP:
        return self.up_side
    elif direction == Dir.DOWN:
        return self.down_side

  def _get_end_side_old(self, direction):
    if direction == Dir.LEFT:
      return self.main_row[0].left_side()
    if direction == Dir.RIGHT:
      return self.main_row[-1].right_side()
    if direction == Dir.UP:
      if self.up:
        return self.up[-1].up_side()
      else:
        return self.spinner.up_side()
    if direction == Dir.DOWN:
      if self.down:
        return self.down[-1].down_side()
      else:
        return self.spinner.down_side()

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

  def add_to_left(self, tile):
    self._set_orientation(tile, Dir.LEFT)
    self.main_row = [tile] + self.main_row
    self._update_spinner(tile)
    self.left_side = tile.left_side()

  def remove_from_left(self):
    removed_tile = self.main_row[0]
    self.main_row = self.main_row[1:]
    if self.spinner and removed_tile == self.spinner:
      self.spinner = None
      self.up_side = None
      self.down_side = None
    if self.main_row:
      self.left_side = self.main_row[0].left_side()

  def add_to_right(self, tile):
    self._set_orientation(tile, Dir.RIGHT)
    self.main_row.append(tile)
    self._update_spinner(tile)
    self.right_side = tile.right_side()

  def remove_from_right(self):
    removed_tile = self.main_row[-1]
    self.main_row = self.main_row[:-1]
    if self.spinner and removed_tile == self.spinner:
      self.spinner = None
      self.up_side = None
      self.down_side = None
    if self.main_row:
      self.right_side = self.main_row[-1].right_side()

  def add_to_top(self, tile):
    self._set_orientation(tile, Dir.UP)
    self.up.append(tile)
    self.up_side = tile.up_side()

  def remove_from_top(self):
    self.up = self.up[:-1]
    if self.up:
        self.up_side = self.up[-1].up_side()
    else:
        self.up_side = self.spinner.small_side

  def add_to_bottom(self, tile):
    self._set_orientation(tile, Dir.DOWN)
    self.down.append(tile)
    self.down_side = tile.down_side()

  def remove_from_bottom(self):
    self.down = self.down[:-1]
    if self.down:
        self.down_side = self.down[-1].down_side()
    else:
        self.down_side = self.spinner.small_side

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
    if direction == Dir.LEFT:
      self.add_to_left(tile)
    elif direction == Dir.RIGHT:
      self.add_to_right(tile)
    elif direction == Dir.UP:
      self.add_to_top(tile)
    elif direction == Dir.DOWN:
      self.add_to_bottom(tile)
    self._update_total_count()
    return self.score()

  def undo_move(self, tile, direction):
    if tile is None:
      return last_move
    if direction == Dir.LEFT:
      self.remove_from_left()
    elif direction == Dir.RIGHT:
      self.remove_from_right()
    elif direction == Dir.UP:
      self.remove_from_top()
    elif direction == Dir.DOWN:
      self.remove_from_bottom()
    self._update_total_count()
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
            self._down_repr() + '\nCount: ' + str(self.total_count))
