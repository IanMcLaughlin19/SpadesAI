import random
import numpy as np
import pyCardDeck
import util
class Agent:
    """
    Taken from Berkely AI, will represent an agent that plays the game
    """
    def __init__(self, index=0):
        self.index = index
        self.hand = []

    def start_episode(self):
        pass

    def update(self, state, action, nextState, reward):
        pass

    def end_episode(self):
        pass

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

    def filter_by_suit(self, suit):
        """
        Helper function to get a list of same suits in hand
        :param suit: one of "Spades", "Diamonds", "Clubs", "Hearts"
        :return: list of cards in hand
        """
        if suit not in ["Spades", "Diamonds", "Clubs", "Hearts"]:
            raise ValueError("Invalid suit kind " + suit)
        return list(filter(lambda card: card.suit == suit, self.hand))

    def filter_by_suit_and_spades(self, suit):
        if suit not in ["Diamonds", "Clubs", "Hearts"]:
            raise ValueError("Invalid suit kind " + suit)
        spades = self.filter_by_suit("Spades")
        other_suit = self.filter_by_suit(suit)
        return spades + other_suit

    def highest_card_by_suit(self, suit):
        cards = self.filter_by_suit(suit)
        return max(cards, key=lambda card: Agent.convert_card_rank_to_int(card))

    def lowest_card_by_suit(self, suit):
        cards = self.filter_by_suit(suit)
        if not cards:
            return []
        return min(cards, key=lambda card: Agent.convert_card_rank_to_int(card))

    def lowest_card_that_wins(self, card_to_beat):
        possible_cards = self.filter_by_suit(card_to_beat.suit)
        possible_winners = list(filter(lambda card: card.rank > card_to_beat.rank, possible_cards))
        if not possible_winners:
            return []
        else:
            return min(possible_winners, key=lambda card: Agent.convert_card_rank_to_int(card))

    def lowest_spade_that_wins(self, card_to_beat):
        if card_to_beat.suit == "Spades":
            return self.lowest_card_that_wins(card_to_beat)
        else:
            return self.lowest_card_by_suit("Spades")

    def highest_non_spade(self):
        non_spades = self.filter_by_suit("Diamonds") + self.filter_by_suit("Hearts") +\
                                  self.filter_by_suit("Clubs")
        if non_spades:
            return max(non_spades, key=lambda card: Agent.convert_card_rank_to_int(card))
        else:
            return []

    def lowest_non_spade(self):
        non_spades = self.filter_by_suit("Diamonds") + self.filter_by_suit("Hearts") +\
                                  self.filter_by_suit("Clubs")
        if non_spades:
            return min(non_spades, key=lambda card: Agent.convert_card_rank_to_int(card))
        else:
            return []

    def non_spade_off_suits(self, suit):
        """
        Will return all cards that are not the same suit or spades
        """

        suits = ["Hearts", "Diamonds", "Clubs"]
        if suit != "Spades":
            suits.remove(suit)
        result = list(filter(lambda card: card.suit in suits, self.hand))
        if not result:
            return []
        else:
            return result

    @staticmethod
    def convert_card_rank_to_int(card: pyCardDeck.PokerCard):
        if card.rank == "J":
            return 11
        elif card.rank == "Q":
            return 12
        elif card.rank == "K":
            return 13
        elif card.rank == "A":
            return 14
        else:
            return int(card.rank)




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


    def __init__(self, index=0, num_training=100, epsilon=.1, alpha=.5, gamma=1, q_values={}):
        Agent.__init__(self, index=index)
        self.episodes_so_far=0.0
        self.accum_train_rewards = 0.0
        self.accum_test_rewards = 0.0
        self.num_training = num_training
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)
        self.q_values_betting = {}
        self.q_values = {}
        self.reward_this_episode = 0
        self.episodes_rewards = {0:0}

    @classmethod
    def create_optimal_agent(cls, index, trained_agent):
        result = QLearningAgent(index=index, epsilon=0, q_values=trained_agent.q_values)
        return result


    def start_episode(self):
        self.reward_this_episode = 0
        max_episodes = max(self.episodes_rewards)
        self.episodes_rewards[max_episodes+1] = 0

    def end_episode(self):
        cur_episode = max(self.episodes_rewards)
        self.episodes_rewards[cur_episode] = self.reward_this_episode

    def make_bet(self, state, num_players=2):
        return RandomAgent.make_bet(self, state)

    def getLegalActions(self, state):
        """
        Will map a limited set of moves to all possible moves based on the state provided
        Actions:
            if no cards on board and not only spades in hand:
                place_highest_non_spade_card
                place_lowest_non_spade_card
            if no cards on board and only spades in hand:
                place_lowest_spade_card
                place_highest_spade_card
            if cards on board:
                if you have same suit:
                    place_highest_same_suit
                    place_lowest_same_suit_that_wins
                    place_lowest_same_suit
                    place_lowest_spade_to_win
                if you don't have same suit:
                    place_lowest_non_spade
                    if you have spades:
                        place_lowest_spade_to_win
                        place_highest_spade_to_win
        """
        possible_ql_moves = []
        if state.cards_on_board():
            lead_card = state.get_lead_card()
            cards_of_same_suit = self.filter_by_suit(lead_card.suit)
            lowest_spade_that_wins = self.lowest_spade_that_wins(lead_card)
            off_suit_non_spades = self.non_spade_off_suits(lead_card.suit)
            has_same_suit = bool(cards_of_same_suit)
            if has_same_suit:
                highest_same_suit = self.highest_card_by_suit(lead_card.suit)
                lowest_same_suit = self.lowest_card_by_suit(lead_card.suit)
                lowest_same_suit_that_wins = self.lowest_card_that_wins(lead_card)
                if highest_same_suit:
                    possible_ql_moves.append("HIGHEST_SAME_SUIT")
                if lowest_same_suit:
                    possible_ql_moves.append("LOWEST_SAME_SUIT")
                if lowest_same_suit_that_wins:
                    possible_ql_moves.append("LOWEST_SAME_SUIT_WIN")
            if lowest_spade_that_wins:
                possible_ql_moves.append("LOWEST_SPADE_WIN")
            if off_suit_non_spades:
                possible_ql_moves.append("LOWEST_OFF_SUIT")
        else:
            non_spades = self.filter_by_suit("Diamonds") + self.filter_by_suit("Hearts") + self.filter_by_suit("Clubs")
            spades = self.filter_by_suit("Spades")
            if non_spades:
                possible_ql_moves.append("HIGHEST_NON_SPADE")
                possible_ql_moves.append("LOWEST_NON_SPADE")
            elif spades:
                possible_ql_moves.append("HIGHEST_SPADE")
                possible_ql_moves.append("LOWEST_SPADE")
        return possible_ql_moves

    def map_legal_actions_to_action(self, legal_action, state):
        lead_card = state.get_lead_card()
        if legal_action == "HIGHEST_SPADE":
            return self.highest_card_by_suit("Spades")
        elif legal_action == "LOWEST_SPADE":
            return self.lowest_card_by_suit("Spades")
        elif legal_action == "HIGHEST_SAME_SUIT":
            return self.highest_card_by_suit(lead_card.suit)
        elif legal_action == "LOWEST_SAME_SUIT":
            return self.lowest_card_by_suit(lead_card.suit)
        elif legal_action == "LOWEST_SAME_SUIT_WIN":
            return self.lowest_card_that_wins(lead_card)
        elif legal_action == "LOWEST_SPADE_WIN":
            return self.lowest_spade_that_wins(lead_card)
        elif legal_action == "HIGHEST_NON_SPADE":
            return self.highest_non_spade()
        elif legal_action == "LOWEST_NON_SPADE" or "LOWEST_OFF_SUIT":
            return self.lowest_non_spade()
        else:
            raise ValueError("Invalid legal action: " + legal_action)

    def getAction(self, state):
        # Pick Actions
        legalActions = self.getLegalActions(state)
        exploration = util.flipCoin(self.epsilon)
        if exploration:
            exploration_action = random.choice(legalActions)
            action = exploration_action
        else:
            exploitation_action = self.getPolicy(state)
            action = exploitation_action
        return action

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if len(actions) == 0:
            return 0.0
        max_val = -9999999
        for action in actions:
            if self.get_q_value(state, action) > max_val:
                max_val = self.get_q_value(state, action)
        return max_val

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        starting_value = self.computeValueFromQValues(state)
        actions = self.getLegalActions(state)
        possible_actions = []
        for action in actions:
            if self.get_q_value(state, action) >= starting_value:
                possible_actions.append(action)
        if len(possible_actions) == 0:
            return None
        return random.choice(possible_actions)

    def update(self, state, action, nextState, reward):
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
        original_q_value = self.get_q_value(state, action)
        next_q_value = self.computeValueFromQValues(nextState)
        updated_q_value = original_q_value + self.alpha * (reward + self.discount * next_q_value - original_q_value)
        self.set_q_values(state, action, updated_q_value)
        self.reward_this_episode += reward

    def set_q_values(self, state, action, updated_q_value):
        state_action_rep = self.create_state_action_rep(state, action)
        self.q_values[state_action_rep] = updated_q_value

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


    def get_q_value(self, state, action):
        """
        For the Q table the first item will be the leading card, followed by cards in the order they are placed.
        The second to last item will be turns remaining
        The last item in the lookup will be the the action i.e "HIGHEST_SPADE" etc.
        There is 6 turns left
        If the board is empty it will be ("EMPTY", 6, "HIGHEST_NON_SPADE") for example
        Cards will be represented as a string with representing with either NS or S indicating non_spade or spade
         + value
        for example a board with a seven of hearts will be "(H7, ACTION)"
        :param state:
        :param action:
        :return:
        """
        state_action = self.create_state_action_rep(state, action)
        if state_action in self.q_values:
            return self.q_values[state_action]
        else:
            return 0.0

    def create_state_action_rep(self, state, action):

        state_action = self.create_board_representation(state) + (action,)
        return state_action

    def create_board_representation(self, state):
        board = state.board
        if not board:
            return ("EMPTY", )
        else:
            result = None
            if len(board) == 1:
                return (self.create_card_representation(list(board.values())[0]), )
            for card in range(len(board)):
                if result is None:
                    result = (self.create_card_representation(list(board.values())[card]), )
                else:
                    result += (self.create_card_representation(list(board.values())[0]), )
        return result


    def create_card_representation(self, card: pyCardDeck.PokerCard):
        representation_dict = {"Spades":"S", "Clubs":"NS", "Diamonds":"NS", "Hearts":"NS"}
        rep = representation_dict[card.suit] + str(card.rank)
        return rep



