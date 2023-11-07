import unittest
from unittest.mock import MagicMock, Mock

"""
Note that for this test I am using an actual battle log statically saved since it felt the easiet way to test the 
BattleParser. As such, we can use a real BattlePokemon object and just in general the design of these unit tests
may feel different In practice we will just ensure that it runs succesfully rather than checking specific things. 

If all the other unit tests work (which is a built in assumption to this module) then this is only responsible for
calling the others correctly as they have already been verified. 
"""

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)
from .battle_data.battle_pokemon import BattlePokemon

# ===bring in object to test===
from . import BattleParser


class TestBattleParser(unittest.TestCase):
    def setUp(self):
        self.mock_battle = TestBattle()
        self.mock_battle.url = "https://replay.pokemonshowdown.com/123-test"
        self.test_battle_pokemon = BattlePokemon(self.mock_battle)

        self.battle_parser = BattleParser(self.mock_battle, self.test_battle_pokemon)

    def test_analyze_battle(self):
        # Call the analyze_battle method
        self.battle_parser.analyze_battle()

        # if we get here then it was succesful
        self.assertTrue(True)

    def test_analyze_battle_error_handling(self):
        # Mock the get_db_info method to raise an exception
        self.battle_parser.battle_data.get_db_info = MagicMock(
            side_effect=Exception("Test exception")
        )

        # Call the analyze_battle method
        self.battle_parser.analyze_battle()

        # Check that self.error is not None
        self.assertIsNotNone(self.battle_parser.error)

        # Check that the error message and traceback are correct
        self.assertEqual(self.battle_parser.error["Error_Message"], "Test exception")
        self.assertIn("Traceback", self.battle_parser.error)


if __name__ == "__main__":
    unittest.main()
