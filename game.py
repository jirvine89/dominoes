import random
from tile import Tile, get_all_tiles, MAX_SIDE_VALUE
from board import Board
from dominoes_util import Dir

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

  def _reset_players(self):
    for player in self.players:
      player.total_score = 0
      player.empty_hand()

  def _next_players_move(self):
    self.turn_index = (self.turn_index + 1) % len(self.players)

  def current_player(self):
    return self.players[self.turn_index]

  def deal_tiles(self):
    for player in self.players:
      player.empty_hand()
    self.board.reset()
    self.last_move = ''
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
    self.last_move += '\nDominoes motha-fucka! %d points' % domino_points
    self._empty_hands()
    self.round_over = True

  def _game_is_blocked_out(self):
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
    self._empty_hands()
    self.turn_index = lowest_player_idx
    self.round_over = True

  def _check_for_win(self):
    for player in self.players:
      if player.total_score >= self.play_to:
        self.last_move += '\nGame over, %s wins' % player.name
        self.game_over = True
        return

  def score_move(self, player):
    if self.board.total_count and self.board.total_count % 5 == 0:
      player.add_score(self.board.total_count)
      self.last_move += ' and scored %d points' % (self.board.total_count)

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
      self.board.make_move(tile, direction, player.name)
      self.score_move(player)
      self.last_move = '%s played tile %s %s' % (player.name, str(tile), direction.name)
      if player.is_out_of_tiles():
        self._domino(player)
      else:
        self._next_players_move()
      self._check_for_win()
      return True

  def draw(self):
    player = self.current_player()
    tile = self.board.draw_from_bone_yard(player.name)
    player.add_tile(tile)
    self.last_move = '%s drew a tile' % player.name #%s' % (player.name, str(tile))

  def knock(self):
    player = self.current_player()
    self.last_move = '%s knocked' % player.name
    self.board.knock(player.name)
    if self._game_is_blocked_out():
      self._score_block_out()
    else:
      self._next_players_move()

  def get_next_move_from_player(self):
    player = self.current_player()
    if player.is_out_of_tiles():
      return 'Game is over. Run game.deal_tiles() to continue with another'
    move = player.pick_move(self.board)
    self.make_move_or_knock(*move)

  def play_round(self, verbose=False):
    self.deal_tiles()
    if verbose:
      print(self)
      print('\n')
    while not self.round_over:
      self.get_next_move_from_player()
      if verbose:
        print(self)
        print('\n')
    if verbose:
      print('\n=== GAME OVER ===')

  def play(self, verbose=False):
    self.start_first_game()
    if verbose:
      print(self)
      print('\n')
    i = 0
    while i < 1000:
      i += 1
      self.get_next_move_from_player()
      if verbose:
        print(self)
        print('\n')
      if self.game_over:
        if verbose:
          print('\n=== GAME OVER ===')
        return [player.total_score for player in self.players]
      if self.round_over:
        self.round_over = False
        self.deal_tiles()
        if verbose:
          print(self)
          print('\n')
    assert False


  def __repr__(self):
    return '%s\nPlayers:\n%s\nTurn:%d\nLast Move: %s' % (str(self.board), str(self.players), self.turn_index+1, self.last_move)
