import sys, getopt
import bots
from player import Player
from game import Game

def play_round(game, bot, p1_name='P1', verbose=False):
    game.deal_tiles()
    game.turn_index = 0
    i = 0
    if verbose:
        print '\n\nNew Game:\n'
    while i < 100:
        # Check if game or round is over
        p1, p2 = game.players
        if game.round_over:
            kept_serve = game.current_player() == p1
            if verbose:
                print kept_serve, p1.total_score - p2.total_score
            return kept_serve, p1.total_score - p2.total_score
        # Get move from bot and make it
        game_state = game.create_game_state()
        bot_move = bot.pick_move(game_state)
        game.make_move_or_knock(*bot_move)
        i += 1
        if verbose:
            print game
            print
    assert False


def main(argv):
    # Read inputs
    if len(argv) < 1:
        print 'starting_value.py <num_rounds>'
        return 1
    opts, args = getopt.getopt(argv[1:], "", ["bot=", "verbose"])
    bot_name = 'GreedyDefensiveBot'
    verbose = False
    for opt, arg in opts:
        if opt == "--bot":
            bot_name = arg
        if opt == "--verbose":
            verbose = True

    # Setup
    num_rounds = int(argv[0])
    play_to = 150
    players = [Player('P1'), Player('P2')]
    bot = getattr(bots, bot_name)()

    # Play rounds
    num_kept_serve, num_lost_serve = 0, 0
    sum_diff_kept_serve, sum_diff_lost_serve = 0., 0.
    for i in range(num_rounds):
        game = Game(players, play_to)
        kept_serve, score_diff = play_round(game, bot, verbose=verbose)
        if kept_serve:
            num_kept_serve += 1
            sum_diff_kept_serve += score_diff
        else:
            num_lost_serve += 1
            sum_diff_lost_serve += score_diff

    # Compute statistics
    avg_diff_kept_serve = (1.0 * sum_diff_kept_serve / num_kept_serve)
    avg_diff_lost_serve = (1.0 * sum_diff_lost_serve / num_lost_serve)
    prob_keep_serve = (1.0 * num_kept_serve / num_rounds)
    print '%.2f avg diff when kept serve' % avg_diff_kept_serve
    print '%.2f avg diff when lost serve' % avg_diff_lost_serve
    print '%.2f%% kept serve' % (100.0 * prob_keep_serve)
    # E(X) = P(C) * (S_C + E(X)) + (1 - P(C)) * S_^C
    # E = P * (S1 + E) + (1 - P) * S2
    # E - P * (S1 + E) = (1 - P) * S2
    # E - P * S1 - P * E = (1 - P) * S2
    # E - P * E - P * S1 = (1 - P) * S2
    # E * (1 - P) - P * S1 = (1 - P) * S2
    # E * (1 - P) = P * S1 + (1 - P) * S2
    # E = (P * S1 + (1 - P) * S2) / (1 - P)
    # E = (P1 * S1 + P2 * S2) / P2
    p1 = prob_keep_serve
    p2 = 1. - prob_keep_serve
    s1 = avg_diff_kept_serve
    s2 = avg_diff_lost_serve
    exp_val = (p1 * s1 + p2 * s2) / p2
    print '%.2f expected value of starting' % exp_val

# RESULTS:
#
# GreedyDefensiveBot, 1k games: 
# 18.63 avg diff when kept serve
# -11.70 avg diff when lost serve
# 57.00% kept serve
# 13.00 expected value of starting
#
# D1TreeBot, 1k games: 
# 19.76 avg diff when kept serve
# -12.20 avg diff when lost serve
# 56.00% kept serve
# 12.94 expected value of starting
#
# D2TreeBot, 100 games:
# 15.58 avg diff when kept serve
# -14.38 avg diff when lost serve
# 60.00% kept serve
# 9.00 expected value of starting
#
# D2TreeBot, 1k games:


if __name__ == "__main__":
    main(sys.argv[1:])
