import algos
import operator as op

class Bot(object):
    def __init__(self, player_name=None):
        self.player_name = player_name

    def pick_move(self, game_state):
        pass

class RandomBot(Bot):
    # ~45 secs for 1k
    def pick_move(self, game_state):
        return algos.pick_random_move(game_state.board, game_state.hand)


class GreedyBot(Bot):
    # vs RandomBot: 74% of 1k
    # ~50 secs for 1k
    def pick_move(self, game_state):
        move, score = algos.pick_greedy_move(game_state.board, game_state.hand)
        return move

class GreedyDefensiveBot(Bot):
    # vs GreedyBot: 59% of 1k
    # vs RandomBot: 83% of 1k
    # ~1 min for 1k
    def pick_move(self, game_state):
        return algos.pick_defensive_move(game_state.board, game_state.hand)

class TreeBot(Bot):
    def __init__(self, depth, player_name=None):
        super(TreeBot, self).__init__(player_name)
        self.depth = depth

    def pick_move(self, game_state):
        ev_dict = algos.tree_search(self.depth, game_state)
        return max(ev_dict.iteritems(), key=op.itemgetter(1))[0]

# 95% CI for 100 trials = 8.5%
# 95% CI for 1k trials = 2.7%
# 95% CI for 10k trials = 0.85%
class D0TreeBot(TreeBot):
    # vs GreedygBot: 50% of 1k
    # ~1 min for 1k games
    def __init__(self, player_name=None):
        super(D0TreeBot, self).__init__(0, player_name)

class D1TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 56% of 1k
    # vs GreedyBot: 69% of 1k
    # ~2 mins for 1k games
    def __init__(self, player_name=None):
        super(D1TreeBot, self).__init__(1, player_name)

class D2TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 64% of 1k
    # vs GreedyBot: 75% of 100
    # vs RandomBot: 91% of 100
    # ~2 mins for 100 games
    def __init__(self, player_name=None):
        super(D2TreeBot, self).__init__(2, player_name)

class D3TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 65% of 1k
    # vs GreedyBot: 69% of 100
    # ~2 secs per game, 25 secs for 10, 4 mins for 100
    def __init__(self, player_name=None):
        super(D3TreeBot, self).__init__(3, player_name)

class D4TreeBot(TreeBot):
    # vs GreedyDefensiveBot: 74% of 100
    # vs GreedyBot: X% of 100
    # ~30 secs per game, 5 mins per 10, 1:25 per 100
    def __init__(self, player_name=None):
        super(D4TreeBot, self).__init__(4, player_name)

