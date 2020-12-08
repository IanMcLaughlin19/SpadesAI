import pickle
import pandas as pd

x1 = pickle.load(open("agentdata/X1QLAGENT_GAMES_100007-19-46-16.p", "rb"))
win_differential_0 = 11
win_differential_1000 = 7
win_differential_2000 = 56
win_differential_5000 = 124
x1_win_differential_1000 = 156
agent25k_win_differential = 145
x_axis = [0, 1000, 2000, 5000, 10000, 25000]
y_axis = [win_differential_0, win_differential_1000, win_differential_2000,
          win_differential_5000, x1_win_differential_1000, agent25k_win_differential]

x = x1.episodes_rewards.keys()
y = x1.episodes_rewards.values()

x2 = pickle.load(open("agentdata/QLAGENT_GAMES_100007-21-15-38.p", "rb"))
import matplotlib.pyplot as plt
agent_25k = pickle.load(open("agentdata/Learning AgentQLAGENT_GAMES_10007-22-12-25.p", "rb"))
def plot_average_reward(agent, window=100):
    df = pd.DataFrame()
    x = agent.episodes_rewards.keys()
    y = list(agent.episodes_rewards.values())
    y.reverse()
    df['keys'] = x
    df['reward'] = y
    df['rolling_reward'] = df['reward'].rolling(window).mean()
    plt.plot(df['keys'], df['rolling_reward'])
    plt.xlabel("Number of training games")
    plt.ylabel("Average reward over last 1000 games")
    plt.title("Average reward per epsiode over " + str(len(x)-1) + "episodes")
    plt.show()
if __name__ == "__main__":
    plot_average_reward(agent_25k)