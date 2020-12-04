import pickle
import matplotlib.pyplot as plt
test_p = pickle.load(open("save.p", "rb"))

keys_sorted = list(test_p.q_values.keys())
keys_sorted.sort(key=lambda key: test_p.q_values[key])
values = []
for key in keys_sorted:
    val = test_p.q_values[key]
    values.append(val)
keys_sorted = list(map(lambda key: str(key), keys_sorted))
x = list(test_p.episodes_rewards.keys())
y = list(test_p.episodes_rewards.values())
N = 3
cumsum, moving_aves = [0], []
import numpy
def running_mean(x, N):
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)
average = list(running_mean(y, 10))
if __name__ == "__main__":
    plt.plot(keys_sorted, values)
    plt.show()

