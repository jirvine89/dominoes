import algos
import operator as op

class Bot(object):
    def __init__(self, player_name=None):
        self.player_name = player_name

    def pick_move(self, game_state):
        pass

class RandomBot(Bot):
    def pick_move(self, game_state):
        return algos.pick_random_move(game_state.board, game_state.hand)


class GreedyBot(Bot):
    def pick_move(self, game_state):
        move, score = algos.pick_greedy_move(game_state.board, game_state.hand)
        return move

class GreedyDefensiveBot(Bot):
    def pick_move(self, game_state):
        return algos.pick_defensive_move(game_state.board, game_state.hand)

class TreeBot(Bot):
    def __init__(self, depth, player_name=None):
        super(TreeBot, self).__init__(player_name)
        self.depth = depth

    def pick_move(self, game_state):
        ev_dict = algos.tree_search(self.depth, game_state)
        return max(ev_dict.iteritems(), key=op.itemgetter(1))[0]

class D0TreeBot(TreeBot):
    # vs GreedyScoringBot: 50% of 1k
    # ~1 min for 1k games
    def __init__(self, player_name=None):
        super(D0TreeBot, self).__init__(0, player_name)

class D1TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 56% of 1k
    # ~5 mins for 1k games
    def __init__(self, player_name=None):
        super(D1TreeBot, self).__init__(1, player_name)

class D2TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 59% of 100
    # ~3 mins for 100 games
    def __init__(self, player_name=None):
        super(D2TreeBot, self).__init__(2, player_name)

class D3TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 66% of 100
    # 15 seconds per game, 3 mins for 10 -> 30 mins for 100
    def __init__(self, player_name=None):
        super(D3TreeBot, self).__init__(3, player_name)

