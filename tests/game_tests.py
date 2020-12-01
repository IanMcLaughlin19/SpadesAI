import unittest
import sys
sys.path.append(r"C:\Users\IANS\PycharmProjects\SpadesAI")
import spades
from agents import Agent

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