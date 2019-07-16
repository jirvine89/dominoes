class GameState(object):
    def __init__(self, board, my_score, opp_score, play_to, hand, opp_hand_size, my_turn=True):
        self.board = board
        self.my_score = my_score
        self.opp_score = opp_score
        self.play_to = play_to
        self.hand = hand
        self.opp_hand_size = opp_hand_size
        self.my_turn = my_turn

    def __repr__(self):
        return ('%s\nHand: %s\nOppHandSize: %d\nScores: [%d, %d] (%d)\nMyTurn:%s'
                % (str(self.board), str(self.hand), self.opp_hand_size, self.my_score,
                self.opp_score, self.play_to, self.my_turn))
