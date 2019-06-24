from player import RandomBot, GreedyScoringBot, GreedyScoringDefensiveBot
from game import Game

def main():
  #player1 = RandomBot('RandomBot')
  player1 = GreedyScoringDefensiveBot('Defensive')
  player2 = GreedyScoringBot('GreedyBot')
  players = [player1, player2]
  
  num_games = 1000
  play_to = 150
  wins = [0 for p in players]
  for i in range(num_games):
    game = Game(players, play_to)
    end_scores = game.play()
    for i, score in enumerate(end_scores):
      if score >= play_to:
        winner_idx = i  
    winner = players[winner_idx]
    wins[winner_idx] += 1
  print(wins)

if __name__ == "__main__":
  main()
