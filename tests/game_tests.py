import unittest
import sys
sys.path.append(r"C:\Users\IANS\PycharmProjects\SpadesAI")
import spades
from agents import Agent, RandomAgent

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


