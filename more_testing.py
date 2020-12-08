import pickle
import matplotlib.pyplot as plt
test_p = pickle.load(open("agentdata/X1QLAGENT_GAMES_100007-19-46-16.p", "rb"))
from spades import Spades
from spades import run_x_games_and_pickle
import spades
import agents
agent_25k = pickle.load(open("agentdata/X2QLAGENT_GAMES_250007-20-50-0.p", "rb"))
agent_10k = pickle.load(open("agentdata/QLAGENT_GAMES_100007-21-1-43.p", "rb"))

if __name__ == "__main__":
    ql = agents.QLearningAgent("test", epsilon=0)
    agent_10k.epsilon = 0
    players = [agent_10k, agents.RandomAgent(2)]
    run_x_games_and_pickle(players, 2000)



