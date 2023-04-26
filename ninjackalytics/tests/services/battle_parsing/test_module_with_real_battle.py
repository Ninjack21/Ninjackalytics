import unittest

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing import (
    BattleParser,
    Battle,
    BattlePokemon,
    ActionData,
    PivotData,
    DamageData,
    HealData,
)

# TODO: Test each module independently with the real battle to confirm code functions in production


class TestBattleMethods(unittest.TestCase):
    def setUp(self):
        self.url = "https://replay.pokemonshowdown.com/gen8ou-1849244413"
        self.battle = Battle(self.url)

    def test_get_id(self):
        expected_id = "gen8ou-1849244413"
        self.assertEqual(self.battle.get_id(), expected_id)

    def test_get_format(self):
        expected_format = "[Gen 8] OU"
        self.assertEqual(self.battle.get_format(), expected_format)

    def test_get_turns(self):
        expected_turns_count = 33
        self.assertEqual(len(self.battle.get_turns()), expected_turns_count)

    def test_get_turn(self):
        turn_num = 3
        turn = self.battle.get_turn(turn_num)
        self.assertIsNotNone(turn)
        self.assertEqual(turn.number, turn_num)


class TestBattlePokemon(unittest.TestCase):
    def setUp(self):
        self.url = "https://replay.pokemonshowdown.com/gen8ou-1849244413"
        self.battle = Battle(self.url)
        self.battle_mons = BattlePokemon(self.battle)

    def test_get_pnum_and_name(self):
        raw_name_from_log = "p2a: Gardevoir"
        expected_pnum = 2
        expected_name = "Gardevoir"
        pnum, name = self.battle_mons.get_pnum_and_name(raw_name_from_log)
        self.assertEqual(pnum, expected_pnum)
        self.assertEqual(name, expected_name)

    def test_get_mon_obj(self):
        p2_gardevoir = "p2a: Gardevoir"
        expected_pnum = 2
        expected_name = "Gardevoir"
        mon = self.battle_mons.get_mon_obj(p2_gardevoir)
        self.assertEqual(mon.player_num, expected_pnum)
        self.assertEqual(mon.real_name, expected_name)

    def test_get_pokemon_current_hp(self):
        p2_gardevoir = "p2a: Gardevoir"
        expected_hp = 100  # all mons start at 100
        hp = self.battle_mons.get_pokemon_current_hp(p2_gardevoir)
        self.assertEqual(hp, expected_hp)

    def test_update_hp_for_pokemon(self):
        p2_gardevoir = "p2a: Gardevoir"
        expected_hp = 50
        self.battle_mons.update_hp_for_pokemon(p2_gardevoir, expected_hp)
        hp = self.battle_mons.get_pokemon_current_hp(p2_gardevoir)
        self.assertEqual(hp, expected_hp)

    def test_get_pokemon_hp_change(self):
        p1_melmetal = "p1a: Melmetal"
        self.battle_mons.update_hp_for_pokemon(p1_melmetal, 50)
        expected_hp_change = -50
        hp_change = self.battle_mons.get_pokemon_hp_change(p1_melmetal)
        self.assertEqual(hp_change, expected_hp_change)

    def test_init_teams(self):
        expected_team_count = 2
        self.assertEqual(len(self.battle_mons.teams), expected_team_count)

        team1 = self.battle_mons.teams[0].pokemon
        expected_teams1_mons = [
            "Dragapult",
            "Urshifu-Rapid-Strike",
            "Tapu Lele",
            "Landorus-Therian",
            "Zapdos",
            "Melmetal",
        ]
        self.assertEqual(len(team1), len(expected_teams1_mons))
        for mon in team1:
            self.assertIn(mon.real_name, expected_teams1_mons)

        team2 = self.battle_mons.teams[1].pokemon
        expected_teams2_mons = [
            "Registeel",
            "Gardevoir",
            "Regigigas",
            "Garchomp",
            "Rotom-Heat",
            "Pelipper",
        ]
        self.assertEqual(len(team2), len(expected_teams2_mons))
        for mon in team2:
            self.assertIn(mon.real_name, expected_teams2_mons)


if __name__ == "__main__":
    unittest.main()
