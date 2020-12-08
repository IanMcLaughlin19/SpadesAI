from agents import RandomAgent, QLearningAgent
from spades import run_x_games_and_pickle




if __name__ == "__main__":
    players_4 = [QLearningAgent("Learning Agent"), RandomAgent("Random1"), RandomAgent("Random2"), RandomAgent("Random3")]
    run_x_games_and_pickle(players_4, 30000, pickle_index=["Learning Agent"])