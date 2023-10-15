import unittest
from datetime import datetime

from . import BattleData

# ===bring in base test utilities objects===
import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
sys.path.insert(1, app_path)
from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)

# ===bring in other real object dependences===
from .battle_pokemon import BattlePokemon


class TestBattleData(unittest.TestCase):
    def setUp(self):
        """
        I need to go find real examples of the different parts of the logs that we care about to
        update these with so that our tests will be used against examples that are realistic.
        """
        self.test_battle = TestBattle()

        self.battle_mons = BattlePokemon(self.test_battle)

        self.battle_data = BattleData(self.test_battle, self.battle_mons)

    def test_get_db_info(self):
        db_info = self.battle_data.get_db_info()
        self.assertIsInstance(db_info, dict)
        self.assertIn("Battle_ID", db_info)
        self.assertEqual(db_info["Battle_ID"], "gen9ou-1954574413")
        self.assertIn("Format", db_info)
        self.assertEqual(db_info["Format"], "gen9ou")
        self.assertIn("P1", db_info)
        self.assertIn("P2", db_info)
        self.assertIn("Rank", db_info)
        self.assertIn("Winner", db_info)
        self.assertIn("Date_Submitted", db_info)
        self.assertIsInstance(db_info["Date_Submitted"], datetime)

    def test_return_general_info(self):
        general_info = self.battle_data._return_general_info()
        self.assertIsInstance(general_info, dict)
        self.assertIn("Battle_ID", general_info)
        self.assertEqual(general_info["Battle_ID"], "gen9ou-1954574413")
        self.assertIn("Format", general_info)
        self.assertEqual(general_info["Format"], "gen9ou")
        self.assertIn("Date_Submitted", general_info)
        self.assertIsInstance(general_info["Date_Submitted"], datetime)

    def test_parse_player_names(self):
        player_names = self.battle_data._parse_player_names()
        self.assertIsInstance(player_names, dict)
        self.assertIn("P1", player_names)
        self.assertEqual(player_names["P1"], "shamasha")

        self.assertIn("P2", player_names)
        self.assertEqual(player_names["P2"], "Xmzx")

    def test_parse_rank(self):
        rank = self.battle_data._parse_rank()
        self.assertIsInstance(rank, dict)
        self.assertIn("Rank", rank)
        self.assertEqual(rank["Rank"], 1307)

    def test_parse_winner(self):
        winner = self.battle_data._parse_winner()
        self.assertIsInstance(winner, dict)
        self.assertIn("Winner", winner)
        self.assertEqual(winner["Winner"], "Xmzx")

    def test_findall_regex(self):
        pattern = r"[0-9]+ \&rarr"
        matches = self.battle_data._findall_regex(pattern)
        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], "1338 &rarr")


if __name__ == "__main__":
    unittest.main()
