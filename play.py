from player import RandomBot, GreedyScoringBot, GreedyScoringDefensiveBot, User
from game import Game

def main():
  player1 = User('Us')
  player2 = GreedyScoringDefensiveBot('Bot')
  players = [player1, player2]
  
  game = Game(players, 150)
  end_scores = game.play(verbose=True)
 
  return end_scores

if __name__ == "__main__":
  main()
