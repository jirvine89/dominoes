import random
from tile import get_all_tiles
from tile import Tile
from collections import defaultdict
from dominoes_util import Dir, all_dirs, opposite

class Player(object):
  def __init__(self, name):
    self.name = name
    self.hand = set()
    self.total_score = 0

  def has_tile(self, tile):
    return tile in self.hand

  def add_tile(self, tile):
    assert not self.has_tile(tile)
    self.hand.add(tile)

  def add_tiles(self, tiles_list):
    for tile in tiles_list:
      self.add_tile(tile)

  def remove_tile(self, tile):
    assert self.has_tile(tile)
    self.hand.remove(tile)

  def empty_hand(self):
    self.hand = set()

  def add_score(self, score):
    self.total_score += score

  def is_out_of_tiles(self):
    return len(self.hand) == 0

  def total_points_in_hand(self):
    total = 0
    for tile in self.hand:
      total += tile.total_points()
    return total

  def can_play(self, board):
    for tile in self.hand:
      for direction in all_dirs():
        if board.valid_move(tile, direction):
          return True
    return False

  def __repr__(self):
    return '%s (%d): %s' % (self.name, self.total_score, str(self.hand))

def is_valid_move_str(move_str):
    if move_str == 'Pass':
        return True
    if (len(move_str) != 3 or
        move_str[0] not in '0123456' or
        move_str[1] not in '0123456' or
        move_str[2] not in 'UDRL'):
        return False
    return True

def parse_move_str(move_str):
    if move_str == 'Pass':
        return None, None
    tile = Tile(int(move_str[0]), int(move_str[1]))
    dir_str = move_str[2]
    if dir_str == 'U':
      direction = Dir.UP
    elif dir_str == 'D':
      direction = Dir.DOWN
    elif dir_str == 'R':
      direction = Dir.RIGHT
    elif dir_str == 'L':
      direction = Dir.LEFT
    else:
      assert False
    return tile, direction



#class CountingChoicesBot(GreedyScoringDefensiveBot):
#  def __init__(self, name):
#    #GreedyScoringDefensiveBot.__init__(self, name) #, self).__init__(name)
#    super(GreedyScoringDefensiveBot, self).__init__(name) #, self).__init__(name)
#    self.total_choices = 1
#
#  def pick_move(self, board):
#    choices = 0
#    moves_made = defaultdict(list)
#    for tile in self.hand:
#      for direction in all_dirs():
#        if board.valid_move(tile, direction):
#          if tile in moves_made.keys():
#            redundant = False
#            for prev_dir in moves_made[tile]:
#              if not board.end_is_double(prev_dir) and not board.end_is_double(direction):
#                redundant = True
#            if redundant: continue
#          moves_made[tile].append(direction)
#          board.make_move(tile, direction, self.name)
#          other_tiles = (set(get_all_tiles()) - set(board.get_tiles_on_board()) - set(self.hand))
#          other_moves_made = defaultdict(list)
#          for other_tile in other_tiles:
#            for other_direction in all_dirs():
#              if board.valid_move(other_tile, other_direction):
#                if other_tile in other_moves_made.keys():
#                  redundant = False
#                  for prev_dir in other_moves_made[other_tile]:
#                    if not board.end_is_double(prev_dir) and not board.end_is_double(other_direction):
#                      redundant = True
#                  if redundant: continue
#                other_moves_made[other_tile].append(other_direction)
#                print(tile, direction, other_tile, other_direction)
#                choices += 1
#          board.undo_last_move()
#    if choices > 0:
#      self.total_choices *= choices
#    print(choices)
#    print(self.total_choices)
#    return super(CountingChoicesBot, self).pick_move(board)
