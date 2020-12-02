import random
import numpy as np
class Agent:
    """
    Taken from Berkely AI, will represent an agent that plays the game
    """
    def __init__(self, index=0):
        self.index = index
        self.hand = []

    def getAction(self, state):
        """
        Return the action that the agent takes
        """
        raise NotImplementedError

    def getLegalActions(self, state):
        """
        Get list of legal actions
        :param state:
        :return: list of legal actinos
        """
        raise NotImplementedError

    def make_bet(self, state, num_players=2):
        """
        :param state:
        :return:
        """
        raise NotImplementedError

class RandomAgent(Agent):

    def getAction(self, state):
        actions = self.getLegalActions(state)
        return random.choice(actions)

    def make_bet(self, state, num_players=2):
        """
        :return: random int from the normal distribution of total rounds / num players
        """
        num_turns = round(52/num_players)
        mu = round(num_turns/2)
        sigma = 2.0
        random_distribution = np.random.randn(100000) * sigma + mu
        bet = round(random.choice(random_distribution))
        if bet > mu * 2:
            bet = mu * 2
        elif bet < 0:
            bet = 0
        return bet

    def getLegalActions(self, state):
        return state.get_legal_moves(self)

class QLearningAgent(Agent):

    def __init__(self, index=0, num_training=100, epsilon=.5, alpha=.5, gamma=1):
        Agent.__init__(index=index)
        self.episodes_so_far=0.0
        self.accum_train_rewards = 0.0
        self.accum_test_rewards = 0.0
        self.num_training = num_training
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)
        self.q_values_betting = {}



    def get_qvalue_betting(self, state_rep, bet: int):
        full_state_rep = state_rep + (bet,)
        if full_state_rep in self.q_values_betting:
            return self.q_values_betting[state_rep]
        else:
            return 0.0

    def compute_value_from_q_values(self, state):
        actions = self.get_legal_bets(state)
        if len(actions) == 0:
            return 0.0
        max_val = -99999999
        for action in actions:
            if self.get_qvalue_betting(state, action) > max_val:
                max_val = self.get_qvalue_betting(state, action)
        return max_val

    def compute_bet_from_q_values(self, state):
        starting_value = self.compute_value_from_q_values(state)
        possible_actions = []
        actions = self.get_legal_bets(state)
        for action in actions:
            if self.get_qvalue_betting(state, action) >= starting_value:
                possible_actions.append(action)
        if len(possible_actions) == 0.0:
            return None
        return random.choice(possible_actions)

    def get_legal_bets(self, state):
        num_players = len(state.players)
        max_bet = round(52/num_players) + 1
        return list(range(0, max_bet))

    def get_state_representation_betting(self):
        """
        For a state representation I will use (combined_value_of_non_spades, combined_value_spades)
        """
        combined_value_non_spades = sum(list(filter(lambda card: card.suit != "Spades", self.hand)))
        combined_value_spades = sum(list(filter(lambda card: card.suit == "Spades", self.hand)))
        return (combined_value_non_spades, combined_value_spades)

    def make_bet(self, state, num_players=2):
        legal_bets = self.get_legal_bets(state)
        exploration = QLearningAgent.flipCoin(self.epsilon)
        if exploration:
            exploration_action = self.make_random_bet(state)
            return exploration_action
        else:
            exploitation_action = self.get_bet_policy(state)
            return exploitation_action

    def make_random_bet(self, state):
        """
        Returns random bet... maybe in the future make it normal distribution around 13 or so
        :param state:
        :return:
        """
        num_players = len(state.players)
        num_turns = round(52/num_players)
        mu = round(num_turns/2)
        sigma = 2.0
        random_distribution = np.random.randn(100000) * sigma + mu
        bet = round(random.choice(random_distribution))
        if bet > mu * 2:
            bet = mu * 2
        elif bet < 0:
            bet = 0
        return bet

    def getLegalActions(self, state):
        return state.get_legal_moves(self)

    def start_episode(self):
        self.last_state = None
        self.last_action = None
        self.episode_rewards = 0.0

    def stop_epsiode(self):
        if self.episodes_so_far < self.num_training:
            self.accum_train_rewards += self.episode_rewards
        else:
            self.accum_test_rewards += self.episode_rewards
        self.episodes_so_far += 1
        if self.episodes_so_far >= self.num_training:
            self.epsilon = 0.0
            self.alpha = 0.0

    def is_in_training(self):
        return self.episodes_so_far < self.num_training

    def is_in_testing(self):
        return not self.is_in_training()

    @staticmethod
    def flipCoin(p):
        r = random.random()
        return r < p

    def get_bet_policy(self, state):
        return self.compute_bet_from_q_values(state)

    def update_betting(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        # Formula for update from slide:
        # Q(s, a) <- q(s,a) + alpha * [R + discount * max_a Q(s'a,) - Q(s,a)]
        # Already know the next q value in this case?
        # TODO: There is a couple formulas for updating throughout text/slides... maybe come back to this at end

        original_q_value = self.get_qvalue_betting(self.get_state_representation_betting(), action)
        next_q_value = self.compute_value_from_q_values(nextState)
        # Maybe check order of operations here
        print("original q:", original_q_value, "nextval:", next_q_value)
        updated_q_value = original_q_value + self.alpha * (reward + self.discount * next_q_value - original_q_value)
        print("State:", str(state), "Action:", str(action), "QValue=", updated_q_value)
        self.q_values_betting[self.get_state_representation_betting() + (action, ) ] = updated_q_value