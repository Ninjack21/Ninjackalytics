import unittest
from unittest.mock import patch, Mock, MagicMock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.pokemon_models import PokemonFinder, Pokemon, Team
from app.services.battle_parsing.battle_pokemon import BattlePokemon


class TestBattlePokemon(unittest.TestCase):
    def setUp(self):
        # Set up a mock battle object
        self.mock_battle = MagicMock()
        self.mock_battle.get_log.return_value = """
            |gen|9
            |poke|p1|Baxcalibur, F|
            |poke|p1|Weavile, F|
            |poke|p1|Espeon, M|
            |poke|p1|Palossand, M|
            |poke|p1|Wo-Chien|
            |poke|p1|Bellibolt, F|
            |poke|p2|Corviknight, M|
            |poke|p2|Iron Thorns|
            |poke|p2|Charizard, M|
            |poke|p2|Grafaiai, F|
            |poke|p2|Flamigo, M|
            |poke|p2|Rotom-Frost|
            |teampreview
            |
            |t:|1677443521
            |start
            |switch|p1a: Esp-nickname|Espeon, M|100/100
            |switch|p2a: Corv-nickname|Corviknight, M, shiny|100/100
            |-ability|p2a: Corviknight|Pressure
            |turn|1
            """

    def test_create_teams(self):
        bp = BattlePokemon(self.mock_battle)
        teams = bp.teams
        self.assertEqual(len(teams), 2)

        # Check that the teams contain the correct Pokemon objects
        alice_team = [p for p in bp.pokemon if p.player_num == 1]
        bob_team = [p for p in bp.pokemon if p.player_num == 2]
        self.assertEqual(len(teams[0].pokemon), len(alice_team))
        self.assertEqual(len(teams[1].pokemon), len(bob_team))

        for i, mon in enumerate(alice_team):
            self.assertEqual(mon, teams[0].pokemon[i])
        for i, mon in enumerate(bob_team):
            self.assertEqual(mon, teams[1].pokemon[i])

    def test_get_mon_obj(self):
        bp = BattlePokemon(self.mock_battle)

        # Test getting a valid Pokemon object
        mon = bp.get_mon_obj("p2a: Charizard")
        self.assertIsInstance(mon, Pokemon)
        self.assertEqual(mon.real_name, "Charizard")
        self.assertEqual(mon.nickname, "Charizard")
        self.assertEqual(mon.player_num, 2)

        # Test getting a non-existent Pokemon object
        with self.assertRaises(ValueError):
            bp.get_mon_obj("p1a: Blastoise")

    def test_update_hp_for_pokemon(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 75.0)

    def test_get_pokemon_hp_change(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_hp_change("p2a: Charizard"), -25)

    def test_get_pokemon_current_hp(self):
        bp = BattlePokemon(self.mock_battle)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 100)

        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 75.0)

    def test_get_pnum_and_name(self):
        bp = BattlePokemon(self.mock_battle)

        raw_name = "p1a: Esp-nickname"
        pnum, name = bp.get_pnum_and_name(raw_name)

        expected_pnum = 1
        expected_name = "Espeon"

        self.assertEqual(pnum, expected_pnum)
        self.assertEqual(name, expected_name)


if __name__ == "__main__":
    unittest.main()
