import pickle
import matplotlib.pyplot as plt
test_p = pickle.load(open("agentdata/QLAGENT_GAMES_100007-18-2-16.p", "rb"))
from spades import Spades
from spades import run_x_games_and_pickle
import spades
import agents

if __name__ == "__main__":
    players = [agents.QLearningAgent(1), agents.RandomAgent(4)]
    run_x_games_and_pickle(players, 100000)


