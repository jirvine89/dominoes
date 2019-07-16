import unittest
import bots
from game import Game
from player import Player
from tournament import play_game

class TestBots(unittest.TestCase):
    def self_play(self, bot_name):
        players = [Player('a'), Player('b')]
        bot1 = getattr(bots, bot_name)('a')
        bot2 = getattr(bots, bot_name)('b')
        game = Game(players, 150)
        end_scores = play_game(game, bot1, bot2)

    def test_random_bot(self):
        self.self_play('RandomBot')

    def test_greedy_bot(self):
        self.self_play('GreedyBot')

    def test_greedy_defensive_bot(self):
        self.self_play('GreedyDefensiveBot')

    def test_d0_tree_bot(self):
        self.self_play('D0TreeBot')

    def test_d1_tree_bot(self):
        self.self_play('D1TreeBot')

    def test_d2_tree_bot(self):
        self.self_play('D2TreeBot')

    #def test_d3_tree_bot(self):
    #    self.self_play('D3TreeBot')

if __name__ == '__main__':
    unittest.main()
