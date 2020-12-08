import random
def flipCoin(p):
    r = random.random()
    return r < p

def save_state(self, state):
    self.last_playing_order = list(map(lambda x: x.index, state.get_playing_order())).index(self.index)
    self.last_score = copy.copy(state.score[self.index])
    self.last_board = copy.copy(state.board)
    self.last_hand = copy._deepcopy_list(self.hand)
    self.num_players = len(state.players)