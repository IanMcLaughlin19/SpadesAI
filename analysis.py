import pickle
import matplotlib.pyplot as plt
test_p = pickle.load(open("QLAGENT_GAMES_50005-16-19-14.p", "rb"))
from spades import Spades
import spades
import agents

if __name__ == "__main__":
    players = [agents.QLearningAgent(1, q_values=test_p.q_values, epsilon=.05),agents.RandomAgent(2)]
    game = spades.Spades(players=players)
    game.play_x_games(500)

