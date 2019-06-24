from player import RandomBot, GreedyScoringBot, GreedyScoringDefensiveBot
from game import Game

def main():
  #player1 = RandomBot('RandomBot')
  player1 = GreedyScoringDefensiveBot('Defensive1')
  player2 = GreedyScoringDefensiveBot('Defensive2')
  players = [player1, player2]
  
  num_rounds = 1000
  delta_sum_kept_serve = 0
  delta_sum_lost_serve = 0
  kept_serve_count = 0
  for i in range(num_rounds):
    game = Game(players, 150)
    game.turn_index = 0
    game.deal_tiles()
    #print(game)
    while not game.round_over:
      game.get_next_move()
    #  print(game)
    score_delta = player1.total_score - player2.total_score
    kept_serve = game.turn_index == 0
    #print ('\n\nGAME %d: %.f and kept serve == %s\n\n' % (i, score_delta, kept_serve))
    if kept_serve:
      delta_sum_kept_serve += score_delta
      kept_serve_count += 1
    else:
      delta_sum_lost_serve += score_delta
  avg_delta_kept_serve = (1.0 * delta_sum_kept_serve / kept_serve_count)
  avg_delta_lost_serve = (1.0 * delta_sum_lost_serve / (num_rounds - kept_serve_count))
  prob_keep_serve = (1.0 * kept_serve_count / num_rounds)
  print '%.2f avg delta when kept serve' % avg_delta_kept_serve
  print '%.2f avg delta when lost serve' % avg_delta_lost_serve
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
  s1 = avg_delta_kept_serve
  s2 = avg_delta_lost_serve
  exp_val = (p1 * s1 + p2 * s2) / p2
  print '%.2f expected value of starting' % exp_val

if __name__ == "__main__":
  main()
