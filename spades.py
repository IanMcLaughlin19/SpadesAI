import pyCardDeck
from typing import List
from agents import Agent
class Spades:

    def __init__(self, players: List[Agent], verbose=False):
        self.deck = pyCardDeck.Deck()
        self.deck.load_standard_deck()
        self.players = players
        self.bets = Spades.initialize_player_dict(players)
        self.scores = Spades.initialize_player_dict(players)
        self.verbose = verbose
        self.initial_state = True
        self.player_won_last_hand = None
        self.board = {}
        self.order_played = {}
        Spades.assert_unique_index(players)

    @classmethod
    def assert_unique_index(cls, players):
        indexes_list = list(map(lambda x: x.index))
        indexes_set = set(indexes_list)
        if not len(indexes_list) == indexes_set:
            raise AssertionError("All players must have a unique index")

    def play_spades(self):
        self.initial_deal()
        self.place_bets()
        while not self.terminal_test():
            self.play_turn()
            self.update_winner()
            self.board = {}
            self.order_played = {}


    def get_legal_moves(self, player: Agent):
        spades_in_hand = list(filter(lambda card: card.suit == "Spades", player.hand))
        count_spades_in_hand = len(spades_in_hand)
        has_other_cards = len(player.hand) != count_spades_in_hand
        if not self.board and has_other_cards:
            return list(filter(lambda card: card.suit != "Spades", player.hand))
        elif not self.board and not has_other_cards:
            return player.hand
        else:
            first_card_suit = self.board[0].suit
            same_suit_cards_in_hand = list(filter(lambda card: card.suit == first_card_suit, player.hand))
            if same_suit_cards_in_hand:
                return same_suit_cards_in_hand + spades_in_hand


    def place_bets(self):
        for player in self.players:
            player_bet = player.make_bet(self)
            self.bets[player.index]= player_bet
            if self.verbose:
                print("Player ", player.index, " places bet ", player_bet)

    def play_turn(self):
        playing_order = self.get_playing_order()
        index = 0
        for player in playing_order:
            action = player.getAction(self)
            self.board[index] = action
            self.order_played[index] = player.index
            if self.verbose:
                print("Player ", player.index, " made move ", str(action))


    def get_playing_order(self):
        if self.player_won_last_hand is None:
            return self.players
        temp_players = self.players.copy()
        starting_player_index = self.players.index(self.player_won_last_hand)
        if starting_player_index == 0:
            return self.players
        else:
            result = []
            result.append(temp_players[starting_player_index - 1:])
            result.append(temp_players[:starting_player_index])
            return result

    @classmethod
    def initialize_player_dict(cls, players:List[Agent]):
        players_dict = {}
        for player in players:
            players_dict[player.index] = 0
        return players_dict

    def terminal_test(self) -> bool:
        """
        Check if game is over. Does this by checking whether any players have cards left
        :return: True if game is over else False
        """
        all_hands_empty = True
        for player in self.players:
            if len(player.hand) != 0:
                all_hands_empty = False
        return all_hands_empty

    def initial_deal(self):
        """
        Runs the initial deal, randomly giving each player cards until there is none left
        :return: None
        """
        while len(self.deck) > 0:
            for player in self.players:
                next_card = self.deck.draw()
                player.hand.append(next_card)
                if self.verbose:
                    print("Player ", player.index, " dealt card ", str(next_card))

    def update_winner(self):
        max_card = None
        winner_index = None
        first_card = self.board[0]
        first_card_suit = first_card.suit
        for card_index in self.board:
            card = self.board[card_index]
            if max_card is None:
                max_card = card
                winner_index = card_index
            elif card.suit == "Spades" and max_card.suit != "Spades":
                max_card = card
                winner_index = card_index
            elif card.suit == first_card_suit and card.rank > first_card.rank:
                max_card = card
                winner_index = card_index
        if max_card is None:
            max_card = first_card
            winner_index = 0
        player_who_won = self.order_played[winner_index]
        self.scores[player_who_won] += 1
        if self.verbose:
            print("Player ", player_who_won, " won turn with card ", str(max_card))








