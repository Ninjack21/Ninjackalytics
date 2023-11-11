import unittest
from unittest.mock import patch, Mock, MagicMock

from .sub_modules import PokemonFinder, Pokemon, Team
from .battle_pokemon import BattlePokemon

# ===bring in base test utilities objects===
import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
sys.path.insert(1, app_path)
from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)


class TestBattlePokemon(unittest.TestCase):
    def setUp(self):
        # Set up a mock battle object
        self.mock_battle = TestBattle()

    def test_create_teams(self):
        bp = BattlePokemon(self.mock_battle)
        teams = bp.teams
        self.assertEqual(len(teams), 2)

        # Check that the teams contain the correct Pokemon objects
        player1_team = [p for p in bp.pokemon if p.player_num == 1]
        player2_team = [p for p in bp.pokemon if p.player_num == 2]
        self.assertEqual(len(teams[0].pokemon), len(player1_team))
        self.assertEqual(len(teams[1].pokemon), len(player2_team))

        for i, mon in enumerate(player1_team):
            self.assertEqual(mon, teams[0].pokemon[i])
        for i, mon in enumerate(player2_team):
            self.assertEqual(mon, teams[1].pokemon[i])

    def test_get_mon_obj(self):
        bp = BattlePokemon(self.mock_battle)

        # Test getting a valid Pokemon object
        mon = bp.get_mon_obj("p1a: Femboy IX")
        self.assertIsInstance(mon, Pokemon)
        self.assertEqual(mon.real_name, "Azumarill")
        self.assertEqual(mon.nickname, "Femboy IX")
        self.assertEqual(mon.player_num, 1)

        # Test getting a non-existent Pokemon object
        with self.assertRaises(ValueError):
            bp.get_mon_obj("p1a: Blastoise")

    def test_update_hp_for_pokemon(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p1a: Femboy IX", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p1a: Femboy IX"), 75.0)

    def test_get_pokemon_hp_change(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p1a: Femboy IX", 75.0)

        self.assertEqual(bp.get_pokemon_hp_change("p1a: Femboy IX"), -25)

    def test_get_pokemon_current_hp(self):
        bp = BattlePokemon(self.mock_battle)

        self.assertEqual(bp.get_pokemon_current_hp("p1a: Femboy IX"), 100)

        bp.update_hp_for_pokemon("p1a: Femboy IX", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p1a: Femboy IX"), 75.0)

    def test_get_pnum_and_name(self):
        bp = BattlePokemon(self.mock_battle)

        raw_name = "p1a: Femboy IX"
        pnum, name = bp.get_pnum_and_name(raw_name)

        expected_pnum = 1
        expected_name = "Azumarill"

        self.assertEqual(pnum, expected_pnum)
        self.assertEqual(name, expected_name)

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
        actual_output = BattlePokemon(
            self.mock_battle
        )._find_function_with_error_from_traceback(tb)
        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()
