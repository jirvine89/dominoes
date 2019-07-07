import random
import math
from tile import get_all_tiles
from tile import Tile
from game import Game
from collections import defaultdict
from dominoes_util import Dir, all_dirs, opposite

def get_valid_moves(board, hand=None):
    valid_moves = []
    if not hand:
        hand = set(get_all_tiles()) - set(board.get_tiles_on_board())
    for tile in hand:
        for direction in all_dirs():
            if board.valid_move(tile, direction):
                valid_moves.append((tile, direction))
    return valid_moves

def pick_random_move(board, hand):
    valid_moves = get_valid_moves(board, hand)
    if not valid_moves:
        return None, None
    random.shuffle(valid_moves)
    return valid_moves[0]

def pick_greedy_move(board, hand):
    best_move = None, None
    best_score = 0
    for tile, direction in get_valid_moves(board, hand):
        board.make_move(tile, direction)
        score = board.score()
        board.undo_move(tile, direction)
        if not best_move[0]:
            best_move, best_score = (tile, direction), score
        elif score > best_score:
            best_move, best_score = (tile, direction), score
    return best_move, best_score

def pick_defensive_move(board, hand):
    greedy_move, greedy_score = pick_greedy_move(board, hand)
    if not greedy_move[0]:
        return None, None
    if greedy_score:
        return greedy_move
    # Otherwise, play defensive move against scores on next turn
    other_tiles = get_other_tiles(board, hand)
    lowest_score_off_move = 100
    for move in get_valid_moves(board, hand):
        best_score_off_move = 0
        board.make_move(*move)
        other_valid_moves = get_valid_moves(board, other_tiles)
        for other_move in other_valid_moves:
             board.make_move(*other_move)
             score = board.score()
             board.undo_move(*other_move)
             if score > best_score_off_move:
                best_score_off_move = score
        board.undo_move(*move)
        if best_score_off_move < lowest_score_off_move:
            lowest_score_off_move = best_score_off_move
            best_move = move
    return best_move


def serve_bonus(score, play_to):
    if score < play_to - 15:
        return score + 12
    if score == play_to - 15:
        return score + 8
    if score == play_to - 10:
        return score + 6
    if score == play_to - 5:
        return score + 4

def i_am_on_serve(hand_size, opp_hand_size, my_turn):
    if not my_turn:
        opp_hand_size -= 1
    return hand_size <= opp_hand_size

def sigmoid(x):
    return math.exp(x) / (1 + math.exp(x))

def sign(x):
    return 1.0 if x >= 0 else -1.0

def z_score(z):
    # TODO: Find actual method for this
    return 1.0  - sigmoid(sign(z) * z ** 2)

def prob_winning_from_scores(my_score, opp_score, play_to):
    # Assuming each score is the same and each player has equal
    # likelihood of scoring, the probability of winning is a 
    # cumulative binomial of Bin(N*P, NP(1-P)). Approximated here
    # using a Z-value of a normal
    avg_score_per_score = 10.
    N = (2 * play_to - my_score - opp_score) / avg_score_per_score
    P = 0.5
    X = (play_to - my_score) / avg_score_per_score
    Z_val = (X - N * P) / (N * P * (1-P))
    return z_score(Z_val)

def get_other_tiles(board, hand):
    return set(get_all_tiles()) - set(hand) - set(board.get_tiles_on_board())

def board_is_boxed_out(board):
    for tile in set(get_all_tiles()) - set(board.get_tiles_on_board()):
        for direction in all_dirs():
            if board.valid_move(tile, direction):
                return False
    return True

def playable_moves(board, tile):
    playable_moves = []
    for direction in all_dirs():
        if board.valid_move(tile, direction):
            playable_moves.append((tile, direction))
    return playable_moves

def simulate_draws(board, hand, boneyard_size):
    other_tiles = get_other_tiles(board, hand)
    extra_tiles = []
    playable_moves_from_draw = []
    while boneyard_size and not playable_moves_from_draw:
        draw_tile = random.sample(other_tiles, 1)
        extra_tiles.append(draw_tile)
        other_tiles.remove(draw_tile)
        boneyard_size -= 1
        playable_moves_from_draw = playable_moves(board, draw_tile)
    return extra_tiles

def compute_prob_draw(num_valid_moves, hand_size, num_total_tiles):
    return

def compute_exp_num_draws(num_valid_moves, hand_size, num_total_tiles):
    # Return 0 if no chance of this happening
    return

def expected_value_opp_moves(move_vals, hand_size, num_total_tiles):
    return

def expected_value_opp_draw(move_vals, prob_draw):
    return prob_draw * mean(move_vals)

def game_state_value(my_score, opp_score, play_to, hand_size, opp_hand_size, my_turn):
    # If game is over, return 1 or 0
    if my_score >= play_to:
        return 1.0
    if opp_score >= play_to:
        return 0.0
    # Adjust scores for serve 
    if i_am_on_serve(hand_size, opp_hand_size, my_turn):
        my_score = serve_bonus(my_score, play_to)
    else:
        opp_score = serve_bonus(opp_score, play_to)
    # Convert scores to probability of winning
    return prob_winning_from_scores(my_score, opp_score, play_to)

def total_points_in_hand(hand):
    return sum([tile.total_points() for tile in hand])

def boxed_out_value(hand, other_tiles, opp_hand_size, my_score, opp_score, play_to):
    pts_in_hand = total_points_in_hand(hand)
    # TODO: This assumes opp is doing no pt management of hand
    pts_in_other_tiles = total_points_in_hand(other_tiles)
    exp_pts_in_opp_hand = 1.0 * opp_hand_size / len(other_tiles)
    # Assumes lowest score gets to serve next
    if pts_in_hand < exp_pts_in_opp_hand:
        my_score += (exp_pts_in_opp_hand / 5) * 5
        my_score += serve_bonus
    elif exp_pts_in_opp_hand < pts_in_hand:
        opp_score += (pts_in_hand / 5) * 5
        opp_score += serve_bonus
    return prob_winning_from_scores(my_score, opp_score, play_to)

def get_valid_moves_and_extra_tiles(board, hand, opp_hand_size):
    valid_moves = get_valid_moves(board, hand)
    # Add empty set to each representing no extra tiles
    valid_moves_and_extra_tiles = zip(valid_moves, [set() for i in len(valid_moves)])
    # If no valid moves, simulate 5 random draws
    if not valid_moves:
        boneyard_size = len(other_tiles) - opp_hand_size
        for i in range(5):
            extra_tiles = simulate_draws(board, hand, boneyard_size)
            valid_moves_after_draw = get_valid_moves(board, set(extra_tiles))
            for move in valid_moves_after_draw:
                # Assumes last tile is the valid move
                valid_moves_and_extra_tiles.append((move, set(extra_tiles[:-1])))
            else: # Knock
                valid_moves_and_extra_tiles.append(((None, None), set(extra_tiles)))

# Searches through tree of moves up to depth given, then uses
# game_state_value
# Assumes making move for whoever's turn it is.
# Returns a dict of expected value of each valid move
# If no valid moves, returns dict from (None, None) to EV
# from drawing.
# TODO:
# * Fill in helper functions above
# * Refactor into smaller chunks
# * Test and get working
def tree_search(depth, board, score, opp_score, play_to, hand, opp_hand_size):
    # If boxed out, score the game
    other_tiles = get_other_tiles(board, hand)
    if board_is_boxed_out(board):
        return {
            (None, None):
            boxed_out_value(hand, other_tiles, opp_hand_size, score, opp_score, play_to)
        }

    # Get valid moves, along with extra tiles form simulation
    valid_moves_and_extra_tiles = get_valid_moves_and_extra_tiles(
        board, hand, opp_hand_size)

    ## Initialize EV_dict and loop through each valid move for keys
    EV_dict = {}
    for move, extra_tiles in valid_moves_and_extra_tiles:
        # Incorporate extra tiles if had to draw before
        hand = hand.union(extra_tiles)
        other_tiles -= extra_tiles
        # Make move, update scoreboard
        move_score = board.make_move(*move)
        hand.remove(tile)
        score += move_score

        # If game over, round over, boxed out OR depth == 0, use game value
        if depth == 0 or len(hand) == 0 or score >= play_to:
            EV_dict[move] = game_state_value(score, opp_score, play_to, len(hand), opp_hand_size, False)
        if board_is_boxed_out(board):
            EV_dict[move] = boxed_out_value(hand, other_tiles, opp_hand_size, score, opp_score, play_to)

        # See if there's a prob of draw. If so, try each move with and without exp num extra opp tiles
        opp_valid_moves = get_valid_moves(board, other_tiles)
        prob_draw = compute_prob_draw(len(opp_valid_moves), opp_hand_size, len(other_tiles))
        exp_num_draws_if_drawing = compute_exp_num_draws(
            len(opp_valid_moves), opp_hand_size, len(other_tiles))

    #    # Loop through opponent's moves, keeping track of value of each
    #    opp_move_vals = []
    #    opp_move_vals_draw = []
    #    for opp_move in opp_valid_moves:
    #        depth -= 1
    #        # Make move, update
    #        opp_move_score = baord.make_move(*opp_move)
    #        opp_score += opp_move_score
    #        opp_hand_size -= 1
    #        # Score move
    #        if opp_hand_size == 0 or depth == 0:
    #            opp_move_vals.append(
    #                game_state_value(score, opp_score, play_to, len(hand), 0, True)
    #        else:
    #            tree_results = tree_search(depth - 1, board, score,
    #                                       opp_score, play_to, hand, opp_hand_size)
    #            opp_move_vals.append(max(tree_results.values()))
    #            if prob_draw:
    #                tree_results_draw = tree_search(depth - 1, board, score, opp_score, play_to,
    #                                                hand, opp_hand_size + exp_num_draws)
    #                opp_move_vals_draw.append(max(tree_results_draw.values()))
    #        # Undo opp move to board, scoreboard, hands, boneyard
    #        opp_hand_size += 1
    #        opp_score -= opp_move_score
    #        board.undo_move(*opp_move)
    #        depth += 1

    #    # Get expected value from these moves
    #    # Sort opponent values, lowest first
    #    # EV_dict[my_move] = dot product of values and probs
    #    ev = expected_value_opp_moves(opp_move_vals, opp_hand_size, len(other_tiles))
    #    ev += expected_value_opp_draw(opp_move_vals_draw, prob_draw)

        # Undo move to board, scoreboard, hand, extra tiles
        board.unde_move(*move)
        hand.add(tile)
        score -= move_score
        hand -= extra_tiles
        other_tiles = other_tiles.union(extra_tiles)

    # If my moves were sims of draws, return the average of all of them
#    if extra_tiles_simulations:
#        return {(None, None): mean(EV_dict.value())}
#    else:
#        return EV_dict


class Algo(object):
    def __init__(self, player_name=None):
        self.player_name = player_name

    def pick_move(self):
        pass

class RandomBot(Algo):
    def pick_move(self, game):
        return pick_random_move(game.board, game.current_player().hand)


class GreedyScoringBot(Algo):
    def pick_move(self, game):
        move, score = pick_greedy_move(game.board, game.current_player().hand)
        return move

class GreedyScoringDefensiveBot(Algo):
  def pick_move(self, game):
    return pick_defensive_move(game.board, game.current_player().hand)
