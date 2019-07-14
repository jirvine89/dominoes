import random
import math
import operator as op
from functools import reduce
from tile import get_all_tiles
from tile import Tile
from game_state import GameState
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

def get_other_tiles(board, hand):
    return set(get_all_tiles()) - set(hand) - set(board.get_tiles_on_board())

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

def total_points_in_hand(hand):
    return sum([tile.total_points() for tile in hand])

def serve_bonus(score, play_to):
    if score < play_to - 15:
        return 12
    else:
        return (play_to - score) / 2.0

def i_am_on_serve(hand_size, opp_hand_size, my_turn):
    if not my_turn:
        opp_hand_size -= 1
    return hand_size <= opp_hand_size

def sigmoid(x):
    if x > 20: return 1.0
    if x < -20: return 0.0
    return math.exp(x) / (1 + math.exp(x))

def sign(x):
    return 1.0 if x >= 0 else -1.0

def z_score(z):
    # TODO: Find actual method for this
    return 1.0 - sigmoid(sign(z) * z ** 2)

def prob_winning_from_scores(my_score, opp_score, play_to):
    # Assuming each score is the same and each player has equal
    # likelihood of scoring, the probability of winning is a 
    # cumulative binomial of Bin(N*P, NP(1-P)). Approximated here
    # using a Z-value of a normal
    if my_score >= play_to:
        return 1.0
    elif opp_score >= play_to:
        return 0.0
    avg_score_per_score = 10.
    N = (2.0 * play_to - my_score - opp_score) / avg_score_per_score
    P = 0.5
    X = 1.0 * (play_to - my_score) / avg_score_per_score
    Z_val = (X - N * P) / (N * P * (1-P))
    return z_score(Z_val)

def game_state_value(gs):
    # If game is over, return 1 or 0
    my_score = gs.my_score
    opp_score = gs.opp_score
    if my_score >= gs.play_to:
        return 1.0
    if opp_score >= gs.play_to:
        return 0.0
    # Adjust scores for serve 
    if i_am_on_serve(len(gs.hand), gs.opp_hand_size, gs.my_turn):
        my_score += serve_bonus(gs.my_score, gs.play_to)
    else:
        opp_score += serve_bonus(gs.opp_score, gs.play_to)
    # Convert scores to probability of winning
    return prob_winning_from_scores(my_score, opp_score, gs.play_to)

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
    # Returns tiles IN ORDER of draws
    other_tiles = get_other_tiles(board, hand)
    extra_tiles = []
    playable_moves_from_draw = []
    while boneyard_size and not playable_moves_from_draw:
        draw_tile = random.sample(other_tiles, 1)[0]
        extra_tiles.append(draw_tile)
        other_tiles.remove(draw_tile)
        boneyard_size -= 1
        playable_moves_from_draw = playable_moves(board, draw_tile)
    return extra_tiles

# TODO: This assumes opp is doing no pt management of hand
def boxed_out_value(gs):
    other_tiles = get_other_tiles(gs.board, gs.hand)
    pts_in_hand = total_points_in_hand(gs.hand)
    pts_in_other_tiles = total_points_in_hand(other_tiles)
    exp_pts_in_opp_hand = 1.0 * pts_in_other_tiles * gs.opp_hand_size / len(other_tiles)
    # Assumes lowest score gets to serve next
    my_score = gs.my_score
    opp_score = gs.opp_score
    if pts_in_hand < exp_pts_in_opp_hand:
        my_score += (int(exp_pts_in_opp_hand) / 5) * 5
        my_score += serve_bonus(my_score, gs.play_to)
    elif exp_pts_in_opp_hand < pts_in_hand:
        opp_score += (pts_in_hand / 5) * 5
        opp_score += serve_bonus(opp_score, gs.play_to)
    return prob_winning_from_scores(my_score, opp_score, gs.play_to)

def get_valid_moves_and_extra_tiles(board, hand, opp_hand_size, sims=5):
    valid_moves = get_valid_moves(board, hand)
    if valid_moves:
        # Add empty set to each representing no extra tiles
        return zip(valid_moves, [set() for i in range(len(valid_moves))])
    else:
        # If no valid moves, simulate 5 random draws
        other_tiles = get_other_tiles(board, hand)
        boneyard_size = len(other_tiles) - opp_hand_size
        valid_moves_and_extra_tiles = []
        for i in range(sims):
            extra_tiles = simulate_draws(board, hand, boneyard_size)
            valid_moves_after_draw = []
            if extra_tiles:
                last_tile = extra_tiles[-1]
                valid_moves_after_draw = playable_moves(board, last_tile)
            for move in valid_moves_after_draw or [(None, None)]:
                valid_moves_and_extra_tiles.append((move, set(extra_tiles)))
        return valid_moves_and_extra_tiles

def ncr(n, r):
    if n <= 0 or r < 0 or n < r: return 0
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer / denom

def compute_prob_draw(num_valid_tiles, hand_size, num_total_tiles):
    #print 'prob'
    #print num_valid_tiles, hand_size, num_total_tiles
    # Num possible hands = Choose(num_total_tiles, hand_size)
    # Num hands with only invalid tiles = Choose(num_invalid_tiles, hand_size)
    num_possible_hands = ncr(num_total_tiles, hand_size)
    num_hands_only_invalid = ncr(num_total_tiles - num_valid_tiles, hand_size)
    prob = 1.0 * num_hands_only_invalid / num_possible_hands
    return prob

def compute_exp_num_draws_given_drawing(num_valid_moves, boneyard_size):
    if num_valid_moves == 0:
        return boneyard_size
    exp = 0.0
    num_tiles_left = boneyard_size
    sum_prev_probs = 0.0
    for i in range(boneyard_size - num_valid_moves + 1):
        prob = (1. - sum_prev_probs) * (1. * num_valid_moves / num_tiles_left)
        exp += (i+1) * prob
        num_tiles_left -= 1
        sum_prev_probs += prob
    return int(round(exp))

def move_dict_to_sorted_list_by_tiles(move_vals):
    tile_vals = {}
    for (tile, direction), val in move_vals.items():
        if not tile in tile_vals.keys():
            tile_vals[tile] = val
        else:
            tile_vals[tile] = min(tile_vals[tile], val)
    return sorted(tile_vals.values())

def expected_value_opp_moves(tile_vals, hand_size, num_total_tiles):
    exp = 0.0
    sum_probs = 0.0
    num_tiles_left = num_total_tiles
    for val in tile_vals:
        prob_is_max = (1 - sum_probs) * (1. * hand_size / num_tiles_left)
        exp += val * prob_is_max
        sum_probs += prob_is_max
        num_tiles_left -= 1
        if num_tiles_left < hand_size:
            break
    return exp

def mean(arr):
    if not arr: return 0.0
    return 1. * sum(arr) / len(arr)

def expected_value_opp_draw(tile_vals, prob_draw):
    return prob_draw * mean(tile_vals)

def tree_inputs_from_game_state(gs):
    return (gs.board, gs.my_score, gs.opp_score, gs.play_to,
            gs.hand, gs.opp_hand_size, gs.my_turn)

# Searches through tree of moves up to depth given, then uses
# game_state_value
# Assumes making move for whoever's turn it is.
# Returns a dict of expected value of each valid move
# If no valid moves, returns dict from (None, None) to EV
# from drawing.
# TODO:
# * Add tree
# * Add E2E tests for this function
# * Refactor into smaller chunks, to fit in 50 lines
def tree_search(depth, game_state, tree_node=None):
    board = game_state.board
    hand = game_state.hand

    # If boxed out, score the game
    other_tiles = get_other_tiles(board, hand)
    if board_is_boxed_out(board):
        return {(None, None): boxed_out_value(game_state)}

    # Get valid moves, along with extra tiles form simulation
    valid_moves_and_extra_tiles = get_valid_moves_and_extra_tiles(
        board, hand, game_state.opp_hand_size)

    # Initialize EV_dict and loop through each valid move for keys
    EV_dict = {}
    used_simulations = False
    for move, extra_tiles in valid_moves_and_extra_tiles:
        if extra_tiles:
            used_simulations = True
        tile, direction = move
        # Incorporate extra tiles if had to draw before
        hand.update(extra_tiles)
        other_tiles -= extra_tiles
        # Make move, update scoreboard
        if tile:
            move_score = board.make_move(tile, direction)
            game_state.my_score += move_score
            hand.remove(tile)

        # If game over, round over, boxed out OR depth == 0, use game value
        if depth == 0 or len(hand) == 0 or game_state.my_score >= game_state.play_to:
            EV_dict[move] = game_state_value(game_state)
        elif board_is_boxed_out(board):
            EV_dict[move] = boxed_out_value(game_state)
        else:
            # See if there's a prob of draw. If so, try each move with and without exp num extra opp tiles
            opp_valid_moves = get_valid_moves(board, other_tiles)
            num_opp_valid_tiles = len(set([m[0] for m in opp_valid_moves]))
            prob_draw = compute_prob_draw(num_opp_valid_tiles, game_state.opp_hand_size, len(other_tiles))
            exp_num_draws_if_drawing = compute_exp_num_draws_given_drawing(
                num_opp_valid_tiles, len(other_tiles) - game_state.opp_hand_size)

            # Loop through opponent's moves, keeping track of value of each
            opp_move_vals = {}
            opp_move_vals_draw = {}
            for opp_move in opp_valid_moves or [(None, None)]:
                opp_tile, opp_direction = opp_move
                #print move, opp_tile, opp_direction
                depth -= 1
                if opp_tile:
                    # Make move, update
                    opp_move_score = board.make_move(opp_tile, opp_direction)
                    game_state.opp_score += opp_move_score
                    game_state.opp_hand_size -= 1
                # Score move
                # TODO: Handle case when board is boxed out?
                if game_state.opp_hand_size == 0 or depth == 0:
                    val = game_state_value(game_state)
                    opp_move_vals[opp_move] = val
                    #if prob_draw:
                    game_state.opp_hand_size += exp_num_draws_if_drawing
                    val_draw = game_state_value(game_state)
                    game_state.opp_hand_size -= exp_num_draws_if_drawing
                    opp_move_vals_draw[opp_move] = val_draw
                else:
                    tree_results = tree_search(depth - 1, game_state)
                    opp_move_vals[opp_move] = max(tree_results.values())
                    #if prob_draw:
                    game_state.opp_hand_size += exp_num_draws_if_drawing
                    tree_results_draw = tree_search(depth - 1, game_state)
                    game_state.opp_hand_size -= exp_num_draws_if_drawing
                    opp_move_vals_draw[opp_move] = max(tree_results_draw.values())
                # Undo opp move to board, scoreboard, hands, boneyard
                if opp_tile:
                    game_state.opp_hand_size += 1
                    game_state.opp_score -= opp_move_score
                    board.undo_move(opp_tile, opp_direction)
                depth += 1

            # Get expected value from these moves
            # Sort opponent values, lowest first
            # EV_dict[my_move] = dot product of values and probs
            opp_tile_vals = move_dict_to_sorted_list_by_tiles(opp_move_vals)
            opp_tile_vals_draw = move_dict_to_sorted_list_by_tiles(opp_move_vals_draw)
            ev = expected_value_opp_moves(opp_tile_vals, game_state.opp_hand_size, len(other_tiles))
            draw_val = expected_value_opp_draw(opp_tile_vals_draw, prob_draw)
            ev += draw_val
            EV_dict[move] = ev

        # Undo move to board, scoreboard, hand, extra tiles
        if tile:
            board.undo_move(tile, direction)
            hand.add(tile)
            game_state.my_score -= move_score
        hand -= extra_tiles
        other_tiles.update(extra_tiles)

    # If my moves were sims of draws, return the average of all of them
    if used_simulations:
        return {(None, None): mean(EV_dict.values())}
    else:
        return EV_dict

