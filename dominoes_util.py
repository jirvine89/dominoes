from enum import Enum

class Orientation(Enum):
  NOT_ON_BOARD = 0
  BIG_UP = 1
  BIG_DOWN = 2
  BIG_LEFT = 3
  BIG_RIGHT = 4
  DOUBLE = 5


class Dir(Enum):
  LEFT = 0
  RIGHT = 1
  UP = 2
  DOWN = 3

def all_dirs():
  return [Dir.LEFT, Dir.RIGHT, Dir.UP, Dir.DOWN]

def opposite(d):
  if d == Dir.LEFT: return Dir.RIGHT
  if d == Dir.RIGHT: return Dir.LEFT
  if d == Dir.UP: return Dir.DOWN
  if d == Dir.DOWN: return Dir.UP

