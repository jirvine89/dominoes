from player import GreedyScoringDefensiveBot, CountingChoicesBot
from game import Game

def main():
  player1 = CountingChoicesBot('Counter')
  player2 = GreedyScoringDefensiveBot('Bot')
  players = [player1, player2]
  
  game = Game(players, 150)
  end_scores = game.play_round(verbose=True)
  print(player1.total_choices / 1e9)
 

if __name__ == "__main__":
  main()
