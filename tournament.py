import sys, getopt
import algos
from player import Player
from game import Game

def play_game(game, bot1, bot2):
    game.start_first_game()
    i = 0
    while i < 1000:
        # Check if game or round is over
        if game.game_over:
            return [player.total_score for player in game.players]
        if game.round_over:
            game.deal_tiles()
            game.round_over = False
        # Get move from bot
        player = game.current_player()
        if player.name == bot1.player_name:
            bot_move = bot1.pick_move(game)
        elif player.name == bot2.player_name:
            bot_move = bot2.pick_move(game)
        else:
            print 'ERROR: no bot with player name %s' % player.name
            assert False
        # Make move on board
        game.make_move_or_knock(*bot_move)
        i += 1
    assert False

def main(argv):
    # Get inputs from command line
    if len(argv) < 1:
        print 'tournament.py <num_games>'
        return 1
    num_games = int(argv[0])
    opts, args = getopt.getopt(argv[1:], "", ["bot1=","bot2=","play_to="])
    bot1_name, bot2_name = "RandomBot", "RandomBot"
    play_to = 150
    for opt, arg in opts:
        if opt == "--bot1":
            bot1_name = arg
        if opt == "--bot2":
            bot2_name = arg
        if opt == "--play_to":
            play_to = arg

    # Set up bots
    player1_name, player2_name = bot1_name, bot2_name
    if bot1_name == bot2_name:
        player1_name, player2_name = bot1_name + '1', bot2_name + '2'
    bot1 = getattr(algos, bot1_name)(player1_name)
    bot2 = getattr(algos, bot2_name)(player2_name)
    print bot1, bot2

    # Play
    players = [Player(player1_name), Player(player2_name)]
    wins = [0 for p in players]
    for i in range(num_games):
        game = Game(players, play_to)
        end_scores = play_game(game, bot1, bot2)
        for i, score in enumerate(end_scores):
          if score >= play_to:
            winner_idx = i
        winner = players[winner_idx]
        wins[winner_idx] += 1

    print(wins)

if __name__ == "__main__":
    main(sys.argv[1:])
