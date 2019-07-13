import unittest
import algos
from board import Board
from game_state import GameState
from tile import Tile, get_all_tiles
from collections import defaultdict
from dominoes_util import Dir, all_dirs, opposite

class TestAlgos(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        moves = [
            (Tile(6,6), Dir.RIGHT),
            (Tile(6,3), Dir.RIGHT),
            (Tile(6,4), Dir.LEFT),
            (Tile(6,0), Dir.UP),
            (Tile(3,3), Dir.RIGHT),
            (Tile(4,5), Dir.LEFT),
            (Tile(5,6), Dir.LEFT),
        ]
        # L: 6
        # R: 3 (double)
        # U: 0
        # D: 6 (spinner)
        # Count: 12
        for tile, direction in moves:
            self.board.make_move(tile, direction)

    def test_get_valid_moves_hand(self):
        hand = set([
            Tile(6, 2),
            Tile(2, 2),
            Tile(3, 1),
            Tile(0, 0)
        ])
        valid_moves = algos.get_valid_moves(self.board, hand)
        expected = [
            (Tile(6, 2), Dir.LEFT),
            (Tile(6, 2), Dir.DOWN),
            (Tile(3, 1), Dir.RIGHT),
            (Tile(0, 0), Dir.UP),
        ]
        self.assertEqual(set(valid_moves), set(expected))

    def test_random_move(self):
        hand = set([
            Tile(6, 2),
            Tile(2, 2),
        ])
        random_moves = [algos.pick_random_move(self.board, hand) for i in range(100)]
        valid_moves = [
            (Tile(6, 2), Dir.LEFT),
            (Tile(6, 2), Dir.DOWN),
        ]
        counts = defaultdict(int)
        for move in random_moves:
            counts[move] += 1
        self.assertTrue(set(counts.keys()) == set(valid_moves))

    def test_greedy_move(self):
        hand = set([
            Tile(3, 4), # Scores 10 Right
            Tile(0, 3), # Scores 15 Up
            Tile(6, 1), # Doesn't score
        ])
        greedy_move, greedy_score = algos.pick_greedy_move(self.board, hand)
        self.assertEquals(greedy_move, (Tile(0,3), Dir.UP))

    def test_greedy_defensive_picks_greedy(self):
        # Test greedy move
        hand = [
            Tile(3, 4), # Scores 10 Right
            Tile(0, 3), # Scores 15 Up
            Tile(6, 1), # Doesn't score
        ]
        defensive_move = algos.pick_defensive_move(self.board, hand)
        self.assertEquals(defensive_move, (Tile(0,3), Dir.UP))

    def test_greedy_defensive_picks_defensive(self):
        self.board.make_move(Tile(3,2), Dir.RIGHT)
        self.board.make_move(Tile(6,2), Dir.RIGHT)
        # Board:
        # L: 6
        # R: 6
        # U: 0
        # D: 6 (spinner)
        # Count: 12
        # Tiles out: (6,6), (6,3), (6,4), (6,0), (3,3), (4,5), (5, 6)
        #  (2,3), (2,6)
        hand = [
            Tile(0, 0), # (0, 3) scores 15
            Tile(0, 4), # (4, 3) scores 15
            Tile(1, 4), # can't play
            Tile(6, 1), # D -> (1, 3) scores 10, R -> no score
            Tile(0, 5), # (5, 3) scores 20
        ]  # Have all 6's
        defensive_move = algos.pick_defensive_move(self.board, hand)
        self.assertTrue(defensive_move in [(Tile(1,6), Dir.RIGHT), (Tile(1,6), Dir.LEFT)])

    def test_prob_winning_from_scores(self):
       self.assertEquals(algos.prob_winning_from_scores(100, 100, 150), 0.5)
       self.assertTrue(algos.prob_winning_from_scores(105, 100, 150) > 0.5)
       self.assertTrue(algos.prob_winning_from_scores(105, 100, 150) < 0.6)
       self.assertAlmostEquals(algos.prob_winning_from_scores(100, 125, 150),
                               1 - algos.prob_winning_from_scores(125, 100, 150))
       self.assertTrue(algos.prob_winning_from_scores(50, 140, 150) < 0.1)
       self.assertTrue(algos.prob_winning_from_scores(145, 140, 150) >
                       algos.prob_winning_from_scores(140, 135, 150))
       self.assertTrue(algos.prob_winning_from_scores(5, 0, 150) < 0.55)
       self.assertTrue(algos.prob_winning_from_scores(112, 115, 150) < 0.5)

    def test_game_state_value(self):
        def build_gs(my_score, opp_score, play_to, hand_size, opp_hand_size, my_turn):
            board = Board()
            hand = set([Tile((i / 7),i % 7) for i in range(hand_size)])
            return GameState(board, my_score, opp_score, play_to,
                             hand, opp_hand_size, my_turn)

        value = algos.game_state_value(build_gs(150, 110, 150, 3, 3, True))
        self.assertEquals(value, 1.0)
        value = algos.game_state_value(build_gs(100, 155, 150, 3, 3, True))
        self.assertEquals(value, 0.0)
        value = algos.game_state_value(build_gs(100, 110, 150, 3, 3, True))
        self.assertGreater(value, 0.5)
        value = algos.game_state_value(build_gs(100, 110, 150, 3, 2, True))
        self.assertLess(value, 0.5)
        value = algos.game_state_value(build_gs(100, 110, 150, 3, 3, False))
        self.assertLess(value, 0.5)
        value = algos.game_state_value(build_gs(100, 115, 150, 3, 3, True))
        self.assertLess(value, 0.5)
        value1 = algos.game_state_value(build_gs(100, 100, 150, 3, 3, True))
        value2 = algos.game_state_value(build_gs(100, 100, 150, 3, 3, False))
        self.assertAlmostEquals(value1, 1.0 - value2)
        value = algos.game_state_value(build_gs(145, 115, 150, 1, 3, True))
        self.assertLess(value, 1.0)

    def test_serve_bonus(self):
        return
        self.assertEquals(100 + algos.serve_bonus(100, 150), 112)
        self.assertEquals(135 + algos.serve_bonus(135, 150), 142.5)
        self.assertEquals(140 + algos.serve_bonus(140, 150), 145)
        self.assertEquals(145 + algos.serve_bonus(145, 150), 147.5)

    def test_i_am_on_serve(self):
        self.assertTrue(algos.i_am_on_serve(5, 5, True))
        self.assertFalse(algos.i_am_on_serve(5, 5, False))
        self.assertTrue(algos.i_am_on_serve(4, 5, True))
        self.assertTrue(algos.i_am_on_serve(4, 5, False))
        self.assertFalse(algos.i_am_on_serve(6, 5, True))

    def test_board_is_boxed_out(self):
        self.assertFalse(algos.board_is_boxed_out(self.board))
        # Create boxed out board
        board = Board()
        moves = [
            (Tile(6,6), Dir.RIGHT),
            (Tile(6,0), Dir.RIGHT),
            (Tile(1,0), Dir.RIGHT),
            (Tile(1,6), Dir.RIGHT),
            (Tile(6,2), Dir.RIGHT),
            (Tile(2,3), Dir.RIGHT),
            (Tile(6,3), Dir.RIGHT),
            (Tile(6,4), Dir.LEFT),
            (Tile(5,4), Dir.LEFT),
            (Tile(5,6), Dir.LEFT),
        ]
        for tile, direction in moves:
            self.assertFalse(algos.board_is_boxed_out(board))
            board.make_move(tile, direction)
        self.assertTrue(algos.board_is_boxed_out(board))

    def test_playable_moves(self):
        # Board:
        # L: 6
        # R: 3 (double)
        # U: 0
        # D: 6 (spinner)
        # Count: 12
        # Tiles out: (6,6), (6,3), (6,4), (6,0), (3,3), (4,5), (5, 6)
        moves_for_0_0 = [(Tile(0,0), Dir.UP)]
        moves_for_0_1 = [(Tile(0,1), Dir.UP)]
        moves_for_2_4 = []
        moves_for_1_6 = [(Tile(1,6), Dir.LEFT), (Tile(1,6), Dir.DOWN)]
        self.assertEqual(algos.playable_moves(self.board, Tile(0,0)),
                         moves_for_0_0)
        self.assertEqual(algos.playable_moves(self.board, Tile(0,1)),
                         moves_for_0_1)
        self.assertEqual(algos.playable_moves(self.board, Tile(2,4)),
                         moves_for_2_4)
        self.assertEqual(algos.playable_moves(self.board, Tile(1,6)),
                         moves_for_1_6)

    def test_simulate_draws(self):
        hand = set([Tile(1,1), Tile(1,2), Tile(1,4), Tile(1,5)])
        boneyard_size = 14
        all_other_tiles = set([
            Tile(0,0), Tile(0,1), Tile(0,2), Tile(0,3), Tile(0,4),
            Tile(0,5), Tile(1,3), Tile(1,6), Tile(2,2), Tile(2,3),
            Tile(2,4), Tile(2,5), Tile(2,6), Tile(3,4), Tile(3,5),
            Tile(4,4), Tile(5,5)])
        # num not playable tiles: 5
        # num playable tiles: 9
        # approximate expected num draws: 1.5
        num_simulations = 100
        sum_draws= 0
        for i in range(num_simulations):
            extra_tiles = algos.simulate_draws(self.board, hand, boneyard_size)
            self.assertGreaterEqual(len(extra_tiles), 0)
            self.assertLessEqual(len(extra_tiles), 6)
            sum_draws += len(extra_tiles)
            for tile in extra_tiles[:-1]:
                self.assertIn(tile, all_other_tiles)
                for direction in all_dirs():
                    self.assertFalse(self.board.valid_move(tile, direction))
            last_tile = extra_tiles[-1]
            self.assertIn(last_tile, all_other_tiles)
            tile_has_valid_move = False
            for direction in all_dirs():
                if self.board.valid_move(last_tile, direction):
                    tile_has_valid_move = True
            self.assertTrue(tile_has_valid_move)
        avg_num_draws = 1.0 * sum_draws / num_simulations
        self.assertLess(avg_num_draws, 1.7)
        self.assertGreater(avg_num_draws, 1.2)

    def test_simulate_draws_until_knock(self):
        # Test case where could draw all tiles
        board = Board()
        moves = [
            (Tile(6,6), Dir.RIGHT),
            (Tile(6,0), Dir.RIGHT),
            (Tile(1,0), Dir.RIGHT),
            (Tile(1,6), Dir.RIGHT),
            (Tile(6,2), Dir.RIGHT),
            (Tile(2,3), Dir.RIGHT),
            (Tile(6,3), Dir.RIGHT),
            (Tile(6,4), Dir.LEFT),
            (Tile(5,4), Dir.LEFT),
            (Tile(5,5), Dir.LEFT),
            (Tile(5,3), Dir.LEFT),
            (Tile(3,0), Dir.LEFT),
            (Tile(0,5), Dir.LEFT),
            (Tile(5,1), Dir.LEFT),
            (Tile(1,2), Dir.LEFT),
            (Tile(2,5), Dir.LEFT),
        ]
        # The only playable tile after this is (5,6)
        for tile, direction in moves:
            board.make_move(tile, direction)
        # 16 tiles out, 12 left over, 4 in each hand, 4 in boneyard
        hand = set([Tile(1,1), Tile(2,2), Tile(3,3), Tile(4,4)])
        boneyard_size = 4
        # 50 / 50 chance of drawing it
        num_knocks = 0
        for i in range(100):
            extra_tiles = algos.simulate_draws(board, hand, boneyard_size)
            can_play = False
            for direction in all_dirs():
                if board.valid_move(extra_tiles[-1], direction):
                    can_play = True
            if can_play:
                self.assertEquals(extra_tiles[-1], Tile(5,6))
                self.assertLessEqual(len(extra_tiles), 4)
            else:
                num_knocks += 1
                self.assertEquals(len(extra_tiles), 4)
        self.assertGreater(num_knocks, 38)
        self.assertLess(num_knocks, 62)


    def test_boxed_out_value(self):
        def build_gs(hand, other_tiles, opp_hand_size, my_score, opp_score, play_to):
            board = Board()
            for tile in get_all_tiles():
                if tile not in hand and tile not in other_tiles:
                    board.add_to_right(tile)
            return GameState(board, my_score, opp_score, play_to, hand, opp_hand_size)

        # They win
        hand = set([Tile(3,3), Tile(4,4)])
        other_tiles = set([Tile(1,1), Tile(0,0), Tile(6,6), Tile(5,5)])
        opp_hand_size = 2
        val = algos.boxed_out_value(build_gs(hand, other_tiles, opp_hand_size, 0, 0, 150))
        self.assertEquals(val, algos.prob_winning_from_scores(0, 22, 150))
        # We win
        hand = set([Tile(2,1), Tile(4,4)])
        val = algos.boxed_out_value(build_gs(hand, other_tiles, opp_hand_size, 0, 0, 150))
        self.assertEquals(val, algos.prob_winning_from_scores(22, 0, 150))
        # Tie
        hand = set([Tile(2,2), Tile(4,4)])
        val = algos.boxed_out_value(build_gs(hand, other_tiles, opp_hand_size, 0, 0, 150))
        self.assertEquals(val, 0.5)

    def test_get_valid_moves_and_extra_tiles_when_valid_moves(self):
        # With valid moves
        hand = [Tile(6, 2), Tile(2, 2), Tile(3, 1), Tile(0, 0)]
        valid_moves = [(Tile(6, 2), Dir.LEFT), (Tile(6, 2), Dir.DOWN),
                       (Tile(3, 1), Dir.RIGHT), (Tile(0, 0), Dir.UP)]
        valid_moves_and_extra_tiles = algos.get_valid_moves_and_extra_tiles(
            self.board, hand, 3)
        expected = [(move, set()) for move in valid_moves]
        self.assertEquals(valid_moves_and_extra_tiles, expected)

    def test_get_valid_moves_and_extra_tiles_when_no_valid_moves(self):
        # With no valid moves
        hand = set([Tile(1,1), Tile(1,2), Tile(1,4), Tile(1,5)])
        valid_moves_and_extra_tiles = algos.get_valid_moves_and_extra_tiles(
            self.board, hand, 3, sims=100)
        self.assertGreaterEqual(len(valid_moves_and_extra_tiles), 100)
        for valid_move, extra_tiles in valid_moves_and_extra_tiles:
            self.assertTrue(valid_move[0])
            self.assertTrue(self.board.valid_move(*valid_move))
            self.assertGreaterEqual(len(extra_tiles), 1)
            num_playable_extra_tiles = 0
            for tile in extra_tiles:
                for direction in all_dirs():
                    if self.board.valid_move(tile, direction):
                        num_playable_extra_tiles += 1
                        break
                        self.assertEquals(tile, valid_move[0])
            self.assertEqual(num_playable_extra_tiles, 1)

    def test_get_valid_moves_and_extra_tiles_when_could_knock(self):
        # Test case where could draw all tiles
        board = Board()
        moves = [
            (Tile(6,6), Dir.RIGHT), (Tile(6,0), Dir.RIGHT), (Tile(1,0), Dir.RIGHT),
            (Tile(1,6), Dir.RIGHT), (Tile(6,2), Dir.RIGHT), (Tile(2,3), Dir.RIGHT),
            (Tile(6,3), Dir.RIGHT), (Tile(6,4), Dir.LEFT), (Tile(5,4), Dir.LEFT),
            (Tile(5,5), Dir.LEFT), (Tile(5,3), Dir.LEFT), (Tile(3,0), Dir.LEFT),
            (Tile(0,5), Dir.LEFT), (Tile(5,1), Dir.LEFT), (Tile(1,2), Dir.LEFT),
            (Tile(2,5), Dir.LEFT),
        ] # The only playable tile after this is (5,6)
        for tile, direction in moves:
            board.make_move(tile, direction)
        # 16 tiles out, 12 left over, 4 in each hand, 4 in boneyard
        hand = set([Tile(1,1), Tile(2,2), Tile(3,3), Tile(4,4)])
        boneyard_size = 4
        valid_moves_and_extra_tiles = algos.get_valid_moves_and_extra_tiles(
            board, hand, boneyard_size, sims=100)
        self.assertGreaterEqual(len(valid_moves_and_extra_tiles), 100)
        no_valid_moves_cnt = 0
        for valid_move, extra_tiles in valid_moves_and_extra_tiles:
            if valid_move[0]:
                self.assertEqual(valid_move[0], Tile(5,6))
                self.assertIn(valid_move[0], extra_tiles)
            else:
                self.assertEqual(len(extra_tiles), 4)
                no_valid_moves_cnt += 1
        self.assertGreaterEqual(no_valid_moves_cnt, 38)
        self.assertLessEqual(no_valid_moves_cnt, 62)

    def test_compute_prob_draw(self):
        # Easy cases
        self.assertEqual(algos.compute_prob_draw(10, 5, 10), 0.0)
        self.assertEqual(algos.compute_prob_draw(6, 5, 10), 0.0)
        self.assertEqual(algos.compute_prob_draw(1, 1, 10), 0.9)
        self.assertEqual(algos.compute_prob_draw(1, 9, 10), 0.1)
        self.assertEqual(algos.compute_prob_draw(0, 10, 10), 1.0)
        # For 3, 5, 10
        prob_miss = 7.0 / 10  # Miss all 3 on first draw
        prob_miss *= 6.0 / 9  # Miss on second draw...
        prob_miss *= 5.0 / 8
        prob_miss *= 4.0 / 7
        prob_miss *= 3.0 / 6
        self.assertAlmostEqual(algos.compute_prob_draw(3, 5, 10), prob_miss)

    def test_compute_exp_num_draws_given_drawing(self):
        # Easy cases
        self.assertEqual(algos.compute_exp_num_draws_given_drawing(5, 5), 1)
        self.assertEqual(algos.compute_exp_num_draws_given_drawing(0, 5), 5)
        # For 1, 3
        exp = (1. / 3) * 1
        exp += (1 - 1. / 3) * (1. / 2) * 2
        exp += (1 - 1. / 3) * (1 - 1. / 2) * (1. / 1) * 3
        self.assertEqual(algos.compute_exp_num_draws_given_drawing(1, 3), int(round(exp)))
        # For 8, 10
        exp = (8. / 10) * 1
        exp += (1 - 8. / 10) * (8. / 9) * 2
        exp += (1 - 8. / 10) * (1 - 8. / 9) * (8. / 8) * 3
        self.assertEqual(algos.compute_exp_num_draws_given_drawing(8, 10), int(round(exp)))

    def test_expected_value_opp_moves_all_valid(self):
        move_vals = [0.7, 0.5, 0.2, 0.2, 0.1]
        # Have all the tiles: max
        self.assertEqual(algos.expected_value_opp_moves(move_vals, 5, 5), 0.7)
        # Have just one tile: avg
        avg = 1. * sum(move_vals) / len(move_vals)
        self.assertAlmostEqual(algos.expected_value_opp_moves(move_vals, 1, 5), avg)
        # Have three tiles: more complicated...
        prob_top = 3. / 5
        exp = prob_top * 0.7
        prob_second = (1 - prob_top) * (3. / 4)
        exp += prob_second * 0.5
        prob_third = (1 - prob_top - prob_second) * (3. / 3)
        exp += prob_third * 0.2
        self.assertAlmostEqual(algos.expected_value_opp_moves(move_vals, 3, 5), exp)

    def test_expected_value_opp_moves_some_invalid(self):
        move_vals = [0.7, 0.5]
        self.assertEqual(algos.expected_value_opp_moves(move_vals, 5, 5), 0.7)
        prob_top = 2. / 5
        exp = prob_top * 0.7
        prob_second = (1 - prob_top) * (2. / 4)
        exp += prob_second * 0.5
        self.assertAlmostEqual(algos.expected_value_opp_moves(move_vals, 2, 5), exp)

    def test_expected_value_opp_draw(self):
        move_vals = [0.7, 0.5]
        self.assertEqual(algos.expected_value_opp_draw(move_vals, 0.2), 0.6 * 0.2)

    def test_tree_search_zero_depth(self):
        hand = set([
            Tile(3, 4), # Scores 10 Right
            Tile(0, 3), # Scores 15 Up
            Tile(6, 1), # Doesn't score
        ])
        gs = GameState(self.board, 0, 0, 150, hand, 4)
        ev_dict = algos.tree_search(0, gs)
        print
        for k, v in ev_dict.items():
            print k, v
        ev_dict = algos.tree_search(1, gs)
        print
        for k, v in ev_dict.items():
            print k, v
        ev_dict = algos.tree_search(1, gs)
        print
        for k, v in ev_dict.items():
            print k, v
        ev_dict = algos.tree_search(1, gs)
        print
        for k, v in ev_dict.items():
            print k, v

# TODO: Add tests for Algo classes, not just functions
# TODO: Add tests for tree_search

if __name__ == '__main__':
    unittest.main()
