import pickle
import matplotlib.pyplot as plt
test_p = pickle.load(open("num_games_20000_3-22-34.p", "rb"))
from spades import Spades
import spades
import agents

if __name__ == "__main__":
    players = [agents.QLearningAgent(1, q_values=test_p.q_values, epsilon=),agents.RandomAgent(2)]
    game = spades.Spades(players=players)
    game.play_x_games(500)

