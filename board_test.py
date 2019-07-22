import unittest
from board import Board
from tile import Tile, get_all_tiles
from dominoes_util import Dir, all_dirs, opposite

class TestBoard(unittest.TestCase):
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

    def test_get_valid_moves(self):
        valid_moves = self.board.get_valid_moves()
        expected = [
            (Tile(6, 1), Dir.LEFT),
            (Tile(6, 2), Dir.LEFT),
            (Tile(6, 1), Dir.DOWN),
            (Tile(6, 2), Dir.DOWN),
            (Tile(0, 0), Dir.UP),
            (Tile(0, 1), Dir.UP),
            (Tile(0, 2), Dir.UP),
            (Tile(0, 3), Dir.UP),
            (Tile(0, 4), Dir.UP),
            (Tile(0, 5), Dir.UP),
            (Tile(3, 0), Dir.RIGHT),
            (Tile(3, 1), Dir.RIGHT),
            (Tile(3, 2), Dir.RIGHT),
            (Tile(3, 4), Dir.RIGHT),
            (Tile(3, 5), Dir.RIGHT),
        ]
        self.assertEqual(set(valid_moves), set(expected))

    def test_get_unique_valid_moves_same(self):
        # Where all valid moves are unique
        valid_moves = self.board.get_unique_valid_moves()
        unique_valid_moves = self.board.get_unique_valid_moves()
        self.assertEqual(set(valid_moves), set(unique_valid_moves))

        # Start of game
        board = Board()
        valid_moves = board.get_unique_valid_moves()
        unique_valid_moves = board.get_unique_valid_moves()
        self.assertEqual(set(valid_moves), set(unique_valid_moves))

        # One tile, not double
        board.make_move(Tile(1,2), Dir.RIGHT)
        valid_moves = board.get_unique_valid_moves()
        unique_valid_moves = board.get_unique_valid_moves()
        self.assertEqual(set(valid_moves), set(unique_valid_moves))

    def test_get_unique_valid_moves_different(self):
        # Test where they differ
        board = Board()
        # Single spinner case
        board.make_move(Tile(6,6), Dir.RIGHT)
        unique_valid_moves = board.get_unique_valid_moves()
        expected = [
            (Tile(6, 0), Dir.RIGHT), (Tile(6, 1), Dir.RIGHT),
            (Tile(6, 2), Dir.RIGHT), (Tile(6, 3), Dir.RIGHT),
            (Tile(6, 4), Dir.RIGHT), (Tile(6, 5), Dir.RIGHT),
        ]
        self.assertEqual(set(unique_valid_moves), set(expected))
        valid_moves = board.get_valid_moves()
        self.assertNotEqual(set(unique_valid_moves), set(valid_moves))
        # Two ends the same
        board.make_move(Tile(6, 5), Dir.RIGHT)
        board.make_move(Tile(6, 4), Dir.LEFT)
        board.make_move(Tile(5, 4), Dir.LEFT)
        unique_valid_moves = board.get_unique_valid_moves()
        expected = [
            (Tile(5, 0), Dir.RIGHT), (Tile(5, 1), Dir.RIGHT),
            (Tile(5, 2), Dir.RIGHT), (Tile(5, 3), Dir.RIGHT),
            (Tile(5, 5), Dir.RIGHT), (Tile(6, 0), Dir.UP),
            (Tile(6, 1), Dir.UP), (Tile(6, 2), Dir.UP),
            (Tile(6, 3), Dir.UP), ]
        self.assertEqual(set(unique_valid_moves), set(expected))
        # Double on one end
        board.make_move(Tile(5,5), Dir.RIGHT)
        unique_valid_moves = board.get_unique_valid_moves()
        expected = [
            (Tile(5, 0), Dir.RIGHT), (Tile(5, 1), Dir.RIGHT),
            (Tile(5, 2), Dir.RIGHT), (Tile(5, 3), Dir.RIGHT),
            (Tile(5, 0), Dir.LEFT), (Tile(5, 1), Dir.LEFT),
            (Tile(5, 2), Dir.LEFT), (Tile(5, 3), Dir.LEFT),
            (Tile(6, 0), Dir.UP), (Tile(6, 1), Dir.UP),
            (Tile(6, 2), Dir.UP), (Tile(6, 3), Dir.UP), ]
        self.assertEqual(set(unique_valid_moves), set(expected))
        # Spinner and single end
        board.make_move(Tile(5,3), Dir.LEFT)
        board.make_move(Tile(6,3), Dir.LEFT)
        unique_valid_moves = board.get_unique_valid_moves()
        expected = [
            (Tile(5, 0), Dir.RIGHT), (Tile(5, 1), Dir.RIGHT),
            (Tile(5, 2), Dir.RIGHT),
            (Tile(6, 0), Dir.UP), (Tile(6, 1), Dir.UP),
            (Tile(6, 2), Dir.UP),
            (Tile(6, 0), Dir.LEFT),
            (Tile(6, 1), Dir.LEFT), (Tile(6, 2), Dir.LEFT)]
        self.assertEqual(set(unique_valid_moves), set(expected))
        # TODO: more tests


if __name__ == '__main__':
    unittest.main()
