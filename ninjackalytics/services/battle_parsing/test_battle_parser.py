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

    def test_find_function_with_error_from_traceback(self):
        tb = """
        Traceback (most recent call last):
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/battle_parser.py", line 42, in analyze_battle
            self.hp_events_handler.handle_events()
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/hp_event_handling/hp_events_handler.py", line 22, in handle_events
            self.damage_data.get_damage_data(line.text, turn)
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/hp_event_handling/damage_models/damages.py", line 70, in get_damage_data
            damage_dict = source_data_finder.get_damage_data(event, turn, self.battle)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/hp_event_handling/damage_models/sub_modules/d_type_specific_models/move.py", line 61, in get_damage_data
            (dealer_num, dealer_name), source = self.dealer_finder.get_dealer_and_source(
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/hp_event_handling/damage_models/sub_modules/dealer_source_finder.py", line 56, in get_dealer_and_source
            return self.move_type_methods[move_type](event, turn, battle)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/hp_event_handling/damage_models/sub_modules/dealer_source_finder.py", line 89, in _get_normal_dealer_and_source
            dealer = self.battle_pokemon.get_pnum_and_name(match.group("dealer"))
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/battle_data/battle_pokemon/battle_pokemon.py", line 58, in get_pnum_and_name
            mon = self.get_mon_obj(raw_name)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jack/Desktop/Ninjackalytics/ninjackalytics/services/battle_parsing/battle_data/battle_pokemon/battle_pokemon.py", line 81, in get_mon_obj
            raise ValueError(f"Could not find a pokemon named {raw_name}")
        ValueError: Could not find a pokemon named p2a: Zoroark
        """
        expected_output = "get_mon_obj"
        actual_output = self.battle_parser._find_function_with_error_from_traceback(tb)
        self.assertEqual(expected_output, actual_output)

    def test_case_where_battle_pokemon_has_error(self):
        # Mock the BattlePokemon object to have an error
        mock_battle_pokemon = Mock()
        mock_battle_pokemon.error = {"Error_Message": "Test error"}
        with self.assertRaises(Exception):
            parser = BattleParser(self.mock_battle, mock_battle_pokemon)

            # Check that parser.error is not None
            self.assertIsNotNone(parser.error)

            # Check that the error message and traceback are correct
            self.assertEqual(parser.error["Error_Message"], "Test error")
            self.assertIn("Traceback", parser.error)


if __name__ == "__main__":
    unittest.main()
