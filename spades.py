import pyCardDeck
from typing import List
from agents import Agent, RandomAgent, QLearningAgent
import random
from copy import deepcopy, copy
from state_representations import QLearningAgentNew, SRStandard

class Spades:

    def __init__(self, players: List[Agent], verbose=False, simple_scoring=False, even_decks=False):
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
        self.even_decks = even_decks
        Spades.assert_unique_index(players)


    @classmethod
    def assert_unique_index(cls, players):
        indexes_list = list(map(lambda x: x.index, players))
        indexes_set = set(indexes_list)
        if not len(indexes_list) == len(indexes_set):
            raise AssertionError("All players must have a unique index")

    def play_x_games(self, num_games=100, even_decks=False):
        score_board = Spades.initialize_player_dict(self.players)
        win_losses = Spades.initialize_player_dict(self.players)
        score_board_last_100 = Spades.initialize_player_dict(self.players)
        round_gone_first_last_100 = Spades.initialize_player_dict(self.players)
        original_index = []
        for p in self.players:
            original_index.append(p.index)
        count_first_player_wins_last_100 = 0
        for game in range(num_games):
            shuffled_first_move = sorted(self.players, key=lambda k: random.random())
            random.shuffle(self.players)
            new_game = Spades(shuffled_first_move, even_decks=even_decks)
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
        restored_order = []
        for p in original_index:
            indexes = list(map(lambda x: x.index, self.players))
            ind = indexes.index(p)
            restored_order.append(self.players[ind])
        self.players = restored_order
        print("Score Board ", str(score_board), " win losses ", str(win_losses))
        return score_board, win_losses

    def play_spades(self):
        for player in self.players:
            player.start_episode()
            player.save_state(self)
        self.initial_deal(self.even_decks)
        self.place_bets()
        while not self.terminal_test():
            self.play_turn()
        self.score_game()
        for player in self.players:
            player.end_episode()
        if self.verbose:
            print("Score ", str(self.scores))
            print("bets ", str(self.bets))
            print("Winner is player ", max(self.final_scores, key=self.final_scores.get), "with score ", max(self.final_scores.values()))

    def play_turn(self):
        playing_order = self.get_playing_order()
        index = 0
        for player in playing_order:
            if type(player) == QLearningAgent or type(player) == QLearningAgentNew:
                last_score = self.scores[player.index]
                player.last_score = last_score
        for player in playing_order:
            if type(player) == QLearningAgent or type(player) == QLearningAgentNew:
                player.last_score = copy(self.scores[player.index])
                action = player.getAction(self)
                last_reward = player.get_last_reward()
                if hasattr(player, "last_score") is not None:
                    player.current_score = self.scores[player.index]
                    player.update(player.get_last_action(), self, last_reward)
                    player.save_state(self)
                player.set_last_action(action)
                test_state = player.create_state_action_rep(self, action)
                card = player.map_legal_actions_to_action(action, self)
            else:
                card = player.getAction(self)
            self.place_card(card, player, index)
            if self.verbose:
                print("Player ", player.index, " made move ", str(card))
            index += 1
        self.update_winner()
        self.board = {}
        self.order_played = {}
        for player in playing_order:
            if type(player) == QLearningAgent or type(player) == QLearningAgentNew:
                reward = self.reward_function(player)
                player.last_reward = reward

    def reward_function(self, agent: Agent):
        max_score = 0
        for player in self.players:
            score = self.scores[player.index]
            if score > max_score:
                max_score = score
        if self.terminal_test():
            if self.scores[agent.index] == max_score:
                reward = 200
            else:
                reward = -250
        else:
            multiplier = agent.get_multiplier_last_action()
            player_score_intial = agent.last_score
            current_score = self.scores[agent.index]
            player_won_turn = current_score > player_score_intial
            if player_won_turn:
                reward = 5 * multiplier
            else:
                reward = -13 * multiplier
        return reward

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

    def initial_deal(self, even_decks = False):
        """
        Runs the initial deal, randomly giving each player cards until there is none left
        :return: None
        """
        if even_decks:
            decks = Spades.create_even_decks()
            players[0].hand = decks[0]
            players[1].hand = decks[1]
        else:
            while len(self.deck) > 0:
                for player in self.players:
                    next_card = self.deck.draw()
                    player.hand.append(next_card)
                    if self.verbose:
                        print("Player ", player.index, " dealt card ", str(next_card))

    @staticmethod
    def create_even_decks():
        deck = pyCardDeck.Deck()
        deck.load_standard_deck()
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]
        suits = ["Spades", "Diamonds", "Clubs", "Hearts"]
        index = 0
        hand1 = []
        hand2 = []
        for r in ranks:
            index +=1
            for suit in suits:
                card = Spades.create_card(suit, r)
                if index % 2 == 0:
                    hand1.append(card)
                else:
                    hand2.append(card)
        return [hand1, hand2]

    @staticmethod
    def create_card(suit, rank):
        return pyCardDeck.PokerCard(suit, rank, "Card")

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
import sys
import os

def run_x_games_and_pickle(players, num_games, pickle_index=[0], directory="agentdata", even_decks=False):
    """
    run many games with players and pickle
    """
    try:
        game = Spades(players)
        game.play_x_games(num_games, even_decks=even_decks)
        for p in players:
            if p.index in pickle_index:
                p.last_state = None
                file_name = directory + "\\" + str(p.index) + "QLAGENT_GAMES_" + str(num_games) + get_time_stamp() + ".p"
                pickle.dump(p, open(file_name, "wb"))
    except KeyboardInterrupt:
        print('Interrupted')
        for pick in pickle_index:
            player = players[pick]
            player.last_state = None
            file_name = directory + "\\" + "QLAGENT_GAMES_" + str(num_games) + get_time_stamp() + ".p"
            pickle.dump(player, open(file_name, "wb"))
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def run_x_games_and_pickle_incrementally(players, games, pickle_index, pickle_increments: list, folder):
    """
    Will run a certain amount of games and save the agent at different points
    :param players: list of players
    :param pickle_index: player indexes to pickle
    :param pickle_increments: increments to pickle at
    :return: will save several agents
    """
    if max(pickle_increments) > games:
        raise ValueError("Pickle index out of bounds, games: {0} increment: {1}".format(games, max(pickle_increments)))
    pickle_increments.sort()
    games_played = 0
    working_directory = os.getcwd()
    target_dir = working_directory + "\\agentdata\\" + folder
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    for increment in pickle_increments:
        difference = increment - games_played
        game = Spades(players)
        game.play_x_games(difference)
        games_played += difference
        for p in players:
            if p.index in pickle_index:
                time_stamp = get_time_stamp()
                full_file_name =target_dir + "\\" + str(p.index) + "_games_played_" + str(games_played) + "_" + time_stamp +".p"
                pickle.dump(p, open(full_file_name, "wb"))
                print("Dumped at ", full_file_name)
import glob
import pandas as pd
def analyze_agents_in_folder(folder, directory=os.getcwd() + "\\agentdata\\", benchmark_games=2000):
    """
    Takes all pick
    :return:
    """
    folder_target = directory + folder + "\\"
    files = glob.glob(folder_target + "*.p")
    df_cols = ["AgentName", "Training Epsiodes", "Win Differential", "Point Differential"]
    df = pd.DataFrame(columns=df_cols)
    for file in files:
        learning_agent = pickle.load(open(file, "rb"))
        file = file.split("\\")[-1]
        split = file.split("_")
        name = split[0]
        games_played = split[3]
        players = [learning_agent, RandomAgent("Random")]
        game = Spades(players=players)
        learning_agent.epsilon = 0
        score_board, win_losses = game.play_x_games(benchmark_games)
        win_dif = win_losses[learning_agent.index] - win_losses['Random']
        score_differential = score_board[learning_agent.index] - score_board['Random']
        data = [name, games_played, win_dif, score_differential]
        new_df = pd.DataFrame(columns=df_cols, data=[data])
        df = pd.concat([df, new_df])
    return df

def get_time_stamp():
    time_stamp = dt.datetime.now()
    day = str(time_stamp.day)
    hour = str(time_stamp.hour)
    minute = str(time_stamp.minute)
    second = str(time_stamp.second)
    full_ft = '-'.join([day, hour, minute, second])
    return full_ft

from state_representations import SRWithTurnsRemaining, SRWithTurnsAndWinning, SRWithTurnsAndSpades, SRWithWinningAndSpades, SRStandard
if __name__ == "__main__":
    final = pd.read_csv("final.csv")
    print("test")





