import unittest
from board.py import Board

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_get_total_count(self):
        #self.assertEqual('foo'.upper(), 'FOO')

    def test_get_end_side(self):
        #self.assertTrue('FOO'.isupper())
        #self.assertFalse('Foo'.isupper())

    def test_end_is_double(self):
        #s = 'hello world'
        #self.assertEqual(s.split(), ['hello', 'world'])
        ## check that s.split fails when the separator is not a string
        #with self.assertRaises(TypeError):
        #    s.split(2)

    def test_orientation_big_side_in_or_out(self):
        return

    def test_get_orientation(self):
        return

    def test_add_to_board(self):
        return

    def test_remove_from_board(self):
        return

    def test_add_and_remove_from_board(self):
        return

    def test_spinner_on_end(self):
        return

    def test_can_play_up_or_down(self):
        return

    def test_valid_move(self):
        return

    def test_make_move(self):
        return

    def test_undo_last_move(self):
        return

    def test_draw_from_boneyard(self):
        return

    def test_consistent_history(self):
        return

if __name__ == '__main__':
    unittest.main()
