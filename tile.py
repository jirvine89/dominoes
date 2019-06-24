from enum import Enum
from dominoes_util import Orientation

MIN_SIDE_VALUE = 0
MAX_SIDE_VALUE = 6

class Tile:
  def __init__(self, side_1, side_2):
    self.small_side = min(side_1, side_2)
    self.big_side = max(side_1, side_2)
    self.orientation = Orientation.NOT_ON_BOARD
  
  def is_double(self):
    return self.small_side == self.big_side

  def total_points(self):
    return self.small_side + self.big_side

  def _dir_side(self, big_orientation, small_orientation):
    if self.orientation == big_orientation:
      return self.big_side
    elif self.orientation == small_orientation:
      return self.small_side
    elif self.orientation == Orientation.DOUBLE:
      return self.small_side
    else:
      assert False

  def _dir_points(self, big_orientation, small_orientation):
    if self.is_double():
      return self.total_points()
    return self._dir_side(big_orientation, small_orientation)

  def left_points(self):
    return self._dir_points(Orientation.BIG_LEFT, Orientation.BIG_RIGHT)
  
  def left_side(self):
    return self._dir_side(Orientation.BIG_LEFT, Orientation.BIG_RIGHT)

  def right_points(self):
    return self._dir_points(Orientation.BIG_RIGHT, Orientation.BIG_LEFT)

  def right_side(self):
    return self._dir_side(Orientation.BIG_RIGHT, Orientation.BIG_LEFT)

  def up_points(self):
    return self._dir_points(Orientation.BIG_UP, Orientation.BIG_DOWN)

  def up_side(self):
    return self._dir_side(Orientation.BIG_UP, Orientation.BIG_DOWN)

  def down_points(self):
    return self._dir_points(Orientation.BIG_DOWN, Orientation.BIG_UP)

  def down_side(self):
    return self._dir_side(Orientation.BIG_DOWN, Orientation.BIG_UP)

  def __repr__(self):
    return '[%d|%d]' % self.ordered_sides()

  def ordered_sides(self):
    ordered_sides = (self.small_side, self.big_side)
    if self.orientation == Orientation.BIG_LEFT or self.orientation == Orientation.BIG_DOWN:
      ordered_sides = (self.big_side, self.small_side)
    return ordered_sides

  def switched_sides(self):
    ordered_sides = self.ordered_sides()
    return ordered_sides[1], ordered_sides[0]
  
  def switched_repr(self):
    return '[%d|%d]' % self.switched_sides()
  
  def __eq__(self, tile):
    return self.small_side == tile.small_side and self.big_side == tile.big_side
  
  def __hash__(self):
    return hash((self.small_side, self.big_side))


def get_all_tiles():
  all_tiles = []
  for i in range(MIN_SIDE_VALUE, MAX_SIDE_VALUE + 1):
    for j in range(i, MAX_SIDE_VALUE + 1):
      tile = Tile(i, j)
      all_tiles.append(tile)
  return all_tiles
