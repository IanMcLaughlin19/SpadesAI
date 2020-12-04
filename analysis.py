import pickle

if __name__ == "__main__":
    test_p = pickle.load(open("save.p", "rb"))
    print(str(test_p.q_values))