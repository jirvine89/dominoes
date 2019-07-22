import random
import copy
from tile import Tile, get_all_tiles, MAX_SIDE_VALUE
from game_state import GameState
from board import Board
from dominoes_util import Dir, Orientation

class Game:
  def __init__(self, players, play_to):
    assert len(players) >= 2 and len(players) <= 4
    names = [player.name for player in players]
    assert len(set(names)) == len(names)
    self.players = players
    self._reset_players()
    self.board = Board()
    self.turn_index = -1
    self.last_move = ''
    self.play_to = play_to
    self.game_over = False
    self.round_over = False
    self.history = []

  def _reset_players(self):
    for player in self.players:
      player.total_score = 0
      player.empty_hand()

  def _next_players_move(self):
    self.turn_index = (self.turn_index + 1) % len(self.players)

  def current_player(self):
    return self.players[self.turn_index]

  def opponent(self):
    # NOTE: assumes 2P
    return self.players[(self.turn_index + 1) % 2]

  def _get_player_and_index_by_name(self, name):
    for i, player in enumerate(self.players):
        if player.name == name:
            return player, i

  def create_game_state(self):
    board = copy.deepcopy(self.board)
    # Assumes 2P
    for player in self.players:
        if player == self.current_player():
            hand = copy.deepcopy(player.hand)
            my_score = player.total_score
        else:
            opp_hand_size = len(player.hand)
            opp_score = player.total_score
    play_to = self.play_to
    return GameState(board, my_score, opp_score, play_to, hand, opp_hand_size)

  def undo_last_move(self):
    if not self.history:
        return
    tile, direction, player_name, score = self.history.pop()
    self.board.undo_move(tile, direction)
    player, idx = self._get_player_and_index_by_name(player_name)
    tile.orientation = Orientation.NOT_ON_BOARD
    player.hand.add(tile)
    player.total_score -= score
    self.turn_index = idx
    if tile:
        self.last_move = 'Undid move %s %s by %s' % (str(tile), direction.name, player.name)
    else:
        # TODO: Handle this better
        self.last_move = 'WARNING: Undid draw by %s, tiles may be wrong!' % player.name
    if score:
        self.last_move += ', which scored %d' % score
    self.game_over = False
    self.round_over = False

  def deal_tiles(self):
    for player in self.players:
      player.empty_hand()
    self.board.reset()
    self.last_move = ''
    self.history = []
    all_tiles = get_all_tiles()
    random.shuffle(all_tiles)
    starting_index = 0
    for player in self.players:
      player.add_tiles(all_tiles[starting_index:starting_index+7])
      starting_index += 7
    self.board.bone_yard = set(all_tiles[starting_index:])

  def start_first_game(self):
    self.deal_tiles()
    for double_val in range(MAX_SIDE_VALUE, -1, -1):
      double_tile = Tile(double_val, double_val)
      for i, player in enumerate(self.players):
        if player.has_tile(double_tile):
          self.turn_index = i
          self.make_move(double_tile, Dir.RIGHT)
          return
    # Redeal and start over
    self.start_first_game()

  def _domino_points(self):
    domino_points = 0
    for player in self.players:
      domino_points += player.total_points_in_hand()
    return domino_points - (domino_points % 5)

  def _block_out_points(self, player_points):
    block_out_points = -1 * player_points
    for player in self.players:
      block_out_points += player.total_points_in_hand()
    return block_out_points - (block_out_points % 5)

  def _empty_hands(self):
    for player in self.players:
      player.empty_hand()

  def _domino(self, player):
    domino_points = self._domino_points()
    player.add_score(domino_points)
    self.last_move += '\nDomino motha-fucka! %d points' % domino_points
    self.round_over = True
    return domino_points

  def game_is_blocked_out(self):
    for player in self.players:
      if player.can_play(self.board):
        return False
    return True

  def _score_block_out(self):
    lowest_score, lowest_player_idx = 12 * 28, -1
    for i, player in enumerate(self.players):
      if player.total_points_in_hand() < lowest_score:
        lowest_score = player.total_points_in_hand()
        lowest_player_idx = i
    block_out_points = self._block_out_points(lowest_score)
    self.players[lowest_player_idx].total_score += block_out_points
    self.last_move += (('\nGame is blocked out, %s has lowest total ' +
                       'points and scores %d points from the rest') %
                       (self.players[lowest_player_idx].name, block_out_points))
    self.turn_index = lowest_player_idx
    self.round_over = True

  def _check_for_win(self):
    for player in self.players:
      if player.total_score >= self.play_to:
        self.last_move += '\nGame over, %s wins' % player.name
        self.game_over = True
        return

  def make_move_or_knock(self, tile, direction):
    if not tile:
      if self.board.tiles_in_bone_yard():
        self.draw()
      else:
        self.knock()
    else:
      self.make_move(tile, direction)

  def make_move(self, tile, direction):
    player = self.current_player()
    if not player.has_tile(tile):
      self.last_move = '%s doesn\'t have tile %s' % (player.name, str(tile))
      return False
    elif not self.board.valid_move(tile, direction):
      self.last_move = 'Can\'t play %s %s' % (str(tile), direction.name)
      return False
    else:
      player.remove_tile(tile)
      score = self.board.make_move(tile, direction) #, player.name)
      self.last_move = '%s played tile %s %s' % (player.name, str(tile), direction.name)
      if score:
        self.last_move += ' and scored %d points' % score
        player.add_score(score)
      if player.is_out_of_tiles():
        domino_points = self._domino(player)
        self.history.append((tile, direction, player.name, score + domino_points))
      else:
        self.history.append((tile, direction, player.name, score))
        self._next_players_move()
      self._check_for_win()
      return True

  def draw(self):
    player = self.current_player()
    tile = self.board.draw_from_bone_yard(player.name)
    player.add_tile(tile)
    self.last_move = '%s drew a tile' % player.name #%s' % (player.name, str(tile))
    self.history.append((None, None, player.name, 0))

  def knock(self):
    player = self.current_player()
    self.last_move = '%s knocked' % player.name
    if self.game_is_blocked_out():
      self._score_block_out()
    else:
      self._next_players_move()


  def __repr__(self):
    return '%s\nPlayers:\n%s\nTurn:%d\nLast Move: %s' % (str(self.board), str(self.players), self.turn_index+1, self.last_move)
