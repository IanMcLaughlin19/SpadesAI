import unittest
import sys
sys.path.append(r"C:\Users\IANS\PycharmProjects\SpadesAI")
import spades
from agents import Agent, RandomAgent, QLearningAgent
import pyCardDeck
from pyCardDeck import PokerCard

class DeckTests(unittest.TestCase):

    def setUp(self) -> None:
        self.test_players = [Agent(), Agent()]

    def test_dealing(self):
        game = spades.Spades(self.test_players)
        for player in self.test_players:
            self.assertEqual(len(player.hand), 0)
        game.initial_deal()
        for player in self.test_players:
            self.assertEqual(len(player.hand), 26)

class GameTests(unittest.TestCase):

    def setUp(self) -> None:
        self.test_players = [RandomAgent(1), RandomAgent(2)]
        self.game = spades.Spades(self.test_players)

    def test_legal_moves_basic(self):
        legal_moves = self.game.get_legal_moves(self.test_players[0])
        self.assertEqual(0, len(legal_moves))

    def test_legal_moves_blank_board(self):
        """
        Tests that on a blank board you can make any move that isn't a Spade
        """
        new_game = spades.Spades(self.test_players.copy())
        new_game.initial_deal()
        legal_moves = self.game.get_legal_moves(self.test_players[0])
        non_spades_in_hand = list(filter(lambda card: card.suit != "Spades", self.test_players[0].hand))
        self.assertEqual(len(legal_moves), len(non_spades_in_hand))
        self.assertGreater(len(legal_moves), 0)

    def test_legal_moves_suit_on_board(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.initial_deal()
        random_card = players[0].getAction(new_game)
        new_game.place_card(random_card, players[0], 0)
        legal_moves = new_game.get_legal_moves(players[1])
        common_suit_and_spades_player_2 = list(filter(lambda card: card.suit == "Spades" or card.suit == random_card.suit, players[1].hand))
        self.assertEqual(len(legal_moves), len(common_suit_and_spades_player_2))
        self.assertGreater(len(legal_moves), 0)

    def test_winner(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.play_spades()
        scores = new_game.scores
        self.assertEqual(1, max(scores.values()))

    def test_update_winner(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        players[0].hand.append(pyCardDeck.PokerCard("Spades", 10, "Ten"))
        players[1].hand.append(pyCardDeck.PokerCard("Spades", 9, "Ten"))
        self.assertDictEqual(new_game.scores, {1:0, 2:0})
        new_game.play_turn()
        new_game.update_winner()
        self.assertDictEqual(new_game.scores, {1:1, 2:0})

    def test_update_winner_2(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        for i in range(20):
            players[0].hand.append(pyCardDeck.PokerCard("Spades", 10, "Ten"))
            players[1].hand.append(pyCardDeck.PokerCard("Spades", 9, "Ten"))
            new_game.play_full_turn()
        self.assertDictEqual(new_game.scores, {1:20, 2:0})

class QLearningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_players = [QLearningAgent(1), RandomAgent(2)]
        self.game = spades.Spades(self.test_players)

    def test_empty_legal_moves(self):
        new_game = spades.Spades(self.test_players.copy())
        empty_actions = self.test_players[0].getLegalActions(new_game)
        self.assertEqual([], empty_actions)

    def test_empty_board_only_spades(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        players[0].hand.append(pyCardDeck.PokerCard("Spades", 7, "Seven"))
        expected = ["HIGHEST_SPADE", "LOWEST_SPADE"]
        actual_actions = self.test_players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual_actions)

    def test_empty_board_spades_and_others(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.initial_deal()
        expected = ["HIGHEST_NON_SPADE", "LOWEST_NON_SPADE"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

    def test_board_with_hearts(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Hearts", 2, "Two")
        players[0].hand.append(pyCardDeck.PokerCard("Hearts", 7, "Seven"))
        expected = ["HIGHEST_SAME_SUIT", "LOWEST_SAME_SUIT", "LOWEST_SAME_SUIT_WIN"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

    def test_board_with_clubs(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Clubs", 2, "Two")
        players[0].hand.append(pyCardDeck.PokerCard("Clubs", 7, "Seven"))
        expected = ["HIGHEST_SAME_SUIT", "LOWEST_SAME_SUIT", "LOWEST_SAME_SUIT_WIN", "LOWEST_OFF_SUIT"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

    def test_lowest_spade_that_wins(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Clubs", 2, "Two")
        players[0].hand.append(pyCardDeck.PokerCard("Clubs", 7, "Seven"))
        players[0].hand.append(pyCardDeck.PokerCard("Spades", 7, "Seven"))
        expected = ["HIGHEST_SAME_SUIT", "LOWEST_SAME_SUIT", "LOWEST_SAME_SUIT_WIN", "LOWEST_SPADE_WIN"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

    def test_only_off_suits(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Clubs", 2, "Two")
        players[0].hand.append(pyCardDeck.PokerCard("Hearts", 7, "Seven"))
        expected = ["LOWEST_OFF_SUIT"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

    def test_real_game(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.initial_deal()
        actual = players[0].getLegalActions(new_game)
        expected = ['HIGHEST_NON_SPADE', 'LOWEST_NON_SPADE']
        self.assertEqual(expected, actual)

    def test_board_rep_empty(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        actual = players[0].create_board_representation(new_game)
        expected = ("EMPTY", )
        self.assertEqual(expected, actual)

    def test_board_rep_one_heart(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Hearts", 2, "Two")
        actual = players[0].create_board_representation(new_game)
        expected = ("H2", )
        self.assertEqual(expected, actual)

    def test_losing_to_spade(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = PokerCard("Spades",3,"Three")
        hand = [PokerCard("Hearts", 7, "Seven")]
        players[0].hand = hand
        expected = ["LOWEST_OFF_SUIT"]
        actual = players[0].getLegalActions(new_game)
        self.assertEqual(expected, actual)

class AgentHelperMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.test_players = [QLearningAgent(1), RandomAgent(2)]
        self.game = spades.Spades(self.test_players)

    def test_lowest_spade_that_wins1(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        seven_spades = pyCardDeck.PokerCard("Spades", 7, "Seven")
        players[0].hand.append(seven_spades)
        new_game.board[0] = pyCardDeck.PokerCard("Spades", 3, "Three")
        actual = players[0].lowest_spade_that_wins(new_game.board[0])
        self.assertEqual(seven_spades, actual)

    def test_lowest_spade_empty(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        new_game.board[0] = pyCardDeck.PokerCard("Spades", 3, "Three")
        actual = players[0].lowest_spade_that_wins(new_game.board[0])
        self.assertEqual([], actual)

    def test_lowest_card_by_suit(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        seven_spades = pyCardDeck.PokerCard("Spades", 7, "Seven")
        players[0].hand.append(seven_spades)
        new_game.board[0] = pyCardDeck.PokerCard("Spades", 3, "Three")
        actual = players[0].lowest_card_that_wins(new_game.board[0])
        self.assertEqual(seven_spades, actual)

    def test_lowest_card_by_suit_empty(self):
        players = self.test_players.copy()
        new_game = spades.Spades(players)
        seven_spades = pyCardDeck.PokerCard("Spades", 7, "Seven")
        new_game.board[0] = pyCardDeck.PokerCard("Spades", 3, "Three")
        actual = players[0].lowest_card_that_wins(new_game.board[0])
        self.assertEqual([], actual)


