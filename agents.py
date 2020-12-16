import random
import numpy as np
import pyCardDeck
import util
import copy
class Agent:
    """
    Taken from Berkely AI, will represent an agent that plays the game
    """
    def __init__(self, index=0):
        self.index = index
        self.hand = []
        self.current_score = 0

    def save_state(self, state):
        pass


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
        possible_winners = list(filter(lambda card: Agent.convert_card_rank_to_int(card) > Agent.convert_card_rank_to_int(card_to_beat), possible_cards))
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

    def lowest_off_suit(self, lead_suit):
        non_spades = self.filter_by_suit("Diamonds") + self.filter_by_suit("Hearts") + \
                     self.filter_by_suit("Clubs")
        non_spades = list(filter(lambda x: x.suit != lead_suit, non_spades))
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
        return 13
        """num_turns = round(52/num_players)
        mu = round(num_turns/2)
        sigma = 2.0
        random_distribution = np.random.randn(100000) * sigma + mu
        bet = round(random.choice(random_distribution))
        if bet > mu * 2:
            bet = mu * 2
        elif bet < 0:
            bet = 0
        return bet"""

    def getLegalActions(self, state):
        return state.get_legal_moves(self)





