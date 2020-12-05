import pyCardDeck
from typing import List
from agents import Agent, RandomAgent, QLearningAgent
import random
from copy import deepcopy
class Spades:

    def __init__(self, players: List[Agent], verbose=False, simple_scoring=False):
        """
        :param players: List of Agents to play a simulated game
        :param verbose: will print out satements on game acitojns
        :param simple_scoring: If true will just score based on who wins the most tricks
        """
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
        self.final_scores = Spades.initialize_player_dict(players)
        self.simple_scoring = simple_scoring
        Spades.assert_unique_index(players)


    @classmethod
    def assert_unique_index(cls, players):
        indexes_list = list(map(lambda x: x.index, players))
        indexes_set = set(indexes_list)
        if not len(indexes_list) == len(indexes_set):
            raise AssertionError("All players must have a unique index")

    def play_x_games(self, num_games=100):
        score_board = Spades.initialize_player_dict(self.players)
        win_losses = Spades.initialize_player_dict(self.players)
        score_board_last_100 = Spades.initialize_player_dict(self.players)
        round_gone_first_last_100 = Spades.initialize_player_dict(self.players)
        count_first_player_wins_last_100 = 0
        for game in range(num_games):
            shuffled_first_move = sorted(self.players, key=lambda k: random.random())
            new_game = Spades(shuffled_first_move)
            new_game.play_spades()
            order_index = 0
            for player in self.players:
                score_board[player.index] += new_game.final_scores[player.index]
                winner = max(new_game.final_scores, key=new_game.final_scores.get)
                if winner == player.index:
                    win_losses[player.index] += 1
                    score_board_last_100[player.index] +=1
                    if order_index == 0:
                        count_first_player_wins_last_100 += 1
                if game % 100 == 0:
                    print("Score board last 100: ", str(score_board_last_100))
                    print("Gone first last 100: ", str(count_first_player_wins_last_100))
                    score_board_last_100 = Spades.initialize_player_dict(self.players)
                    round_gone_first_last_100 = 0
                if order_index == 0:
                    pass
                    #round_gone_first_last_100[player.index] += 1
                order_index += 1
            if game % 20 == 0:
                print("Games completed: ", game)
        print("Score Board ", str(score_board), " win losses ", str(win_losses))

    def play_spades(self):
        for player in self.players:
            player.start_episode()
        self.initial_deal()
        self.place_bets()
        while not self.terminal_test():
            self.play_full_turn()
        self.score_game()
        for player in self.players:
            player.end_episode()
        if self.verbose:
            print("Score ", str(self.scores))
            print("bets ", str(self.bets))
            print("Winner is player ", max(self.final_scores, key=self.final_scores.get), "with score ", max(self.final_scores.values()))

    def play_full_turn(self):
        self.play_turn()
        self.update_winner()
        self.board = {}
        self.order_played = {}
    def score_game(self):
        for player in self.players:
            player_bet = self.bets[player.index]
            player_score = self.scores[player.index]
            if not self.simple_scoring:
                if player_bet > player_score:
                    continue
                elif player_bet == player_score:
                    self.final_scores[player.index] = player_bet * 10
                elif player_bet < player_score:
                    difference = player_score - player_bet
                    self.final_scores[player.index] = player_bet * 10 - (difference * 10)
            else:
                self.final_scores[player.index] = player_score * 10

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
            else:
                return player.hand


    def place_bets(self):
        for player in self.players:
            player_bet = player.make_bet(self, num_players=len(self.players))
            self.bets[player.index] = player_bet
            if self.verbose:
                print("Player ", player.index, " places bet ", player_bet)

    def play_turn(self):
        playing_order = self.get_playing_order()
        index = 0
        for player in playing_order:
            if type(player) == QLearningAgent:
                original_state = deepcopy(self)
                action = player.getAction(self)
                card = player.map_legal_actions_to_action(action, self)
            else:
                card = player.getAction(self)
            self.place_card(card, player, index)
            if self.verbose:
                print("Player ", player.index, " made move ", str(card))
            index += 1

        for player in playing_order:
            reward = self.reward_function(player)
            player.update(original_state, action, self, reward)

    def reward_function(self, agent: Agent):
        max_score = 0
        for player in self.players:
            score = self.scores[player.index]
            if score > max_score:
                max_score = score
        if self.terminal_test():
            if self.scores[agent.index] == max_score:
                reward = 100
            else:
                reward = -100
        else:
            reward = -5
        return reward



    def place_card(self, card, player, index):
        player.hand.remove(card)
        self.board[index] = card
        self.order_played[index] = player.index


    def get_playing_order(self):
        if self.player_won_last_hand is None:
            return self.players
        else:
            temp_players = self.players.copy()
            starting_player = temp_players.index(self.player_won_last_hand)
            result = []
            count = starting_player
            for i in range(len(temp_players)):
                try:
                    result.append(temp_players[count])
                except IndexError:
                    count = 0
                    result.append(temp_players[count])
                count += 1
            return result

    def get_player_by_index(self, index):
        for p in self.players:
            if p.index == index:
                return p


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
            elif card.suit == first_card_suit and\
                    Agent.convert_card_rank_to_int(card) > Agent.convert_card_rank_to_int(first_card):
                max_card = card
                winner_index = card_index
        if max_card is None:
            max_card = first_card
            winner_index = 0
        player_who_won = self.order_played[winner_index]
        self.player_won_last_hand = self.get_player_by_index(player_who_won)
        self.scores[player_who_won] += 1
        if self.verbose:
            print("Player ", player_who_won, " won turn with card ", str(max_card))

    def cards_on_board(self):
        return bool(self.board)

    def get_lead_card(self):
        if not self.cards_on_board():
            return AssertionError("No cards on board")
        return self.board[0]


import pickle
import datetime as dt
import numpy as np

def run_x_games_and_pickle(players, num_games, pickle_index=[0]):
    """
    run many games with players and pickle
    """
    game = Spades(players)
    game.play_x_games(num_games)
    for pick in pickle_index:
        file_name = "QLAGENT_GAMES_" + str(num_games) + get_time_stamp() +".p"
        pickle.dump(players[pick], open(file_name, "wb"))



def get_time_stamp():
    time_stamp = dt.datetime.now()
    day = str(time_stamp.day)
    hour = str(time_stamp.hour)
    minute = str(time_stamp.minute)
    second = str(time_stamp.second)
    full_ft = '-'.join([day, hour, minute, second])
    return full_ft

if __name__ == "__main__":
    players = [QLearningAgent(1), RandomAgent(2)]
    run_x_games_and_pickle(players, 5000)




