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

url = "https://replay.pokemonshowdown.com/gen8ou-1849244413"
battle = Battle(url)
battle_pokemon = BattlePokemon(battle)


class TestBattle(unittest.TestCase):
    def setUp(self):
        self.url = "https://replay.pokemonshowdown.com/gen8ou-1849244413"
        self.battle = battle

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
        self.battle = battle
        self.battle_mons = battle_pokemon

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


class TestActionData(unittest.TestCase):
    def setUp(self):
        self.battle = battle
        self.data_finder = ActionData(self.battle)

    def test_get_action_data(self):
        turn_actions = self.data_finder.get_action_data()
        # 33 turns x 2 actions / turn
        self.assertEqual(len(turn_actions), 66)

        turn1_actions = [action for action in turn_actions if action["Turn"] == 1]
        # should only be 1 action / player
        self.assertEqual(len(turn1_actions), 2)

        p1_action = [
            action for action in turn1_actions if action["Player_Number"] == 1
        ][0]
        p2_action = [
            action for action in turn1_actions if action["Player_Number"] == 2
        ][0]

        self.assertEqual(p1_action["Action"], "move")
        self.assertEqual(p2_action["Action"], "move")


class TestPivotData(unittest.TestCase):
    def setUp(self):
        self.battle = battle
        self.battle_pokemon = battle_pokemon
        self.data_finder = PivotData(self.battle, self.battle_pokemon)

    def test_get_pivot_data(self):
        pivots = self.data_finder.get_pivot_data()
        # 21 |switch| instances found in log with cmd + f
        self.assertEqual(len(pivots), 21)

        turn0_pivots = [pivot for pivot in pivots if pivot["Turn"] == 0]
        # should only be 1 action / player
        self.assertEqual(len(turn0_pivots), 2)

        p1_pivot = [pivot for pivot in turn0_pivots if pivot["Player_Number"] == 1][0]
        p2_pivot = [pivot for pivot in turn0_pivots if pivot["Player_Number"] == 2][0]

        self.assertEqual(p1_pivot["Pokemon_Enter"], "Zapdos")
        self.assertEqual(p1_pivot["Source_Name"], "action")

        self.assertEqual(p2_pivot["Pokemon_Enter"], "Gardevoir")
        self.assertEqual(p2_pivot["Source_Name"], "action")


class TestDamageData(unittest.TestCase):
    def setUp(self):
        self.battle = battle
        self.battle_pokemon = battle_pokemon
        self.data_finder = DamageData(self.battle, self.battle_pokemon)

    def test_get_damage_data(self):
        damages = self.data_finder.get_all_damage_data()

        # 39 |damage| instances found in log with cmd + f
        self.assertEqual(len(damages), 39)

        # only one damage event in turn 1
        turn1_damage_event = [damage for damage in damages if damage["Turn"] == 1][0]

        self.assertEqual(turn1_damage_event["Damage"], 40)
        self.assertEqual(turn1_damage_event["Source_Name"], "Volt Switch")
        self.assertEqual(turn1_damage_event["Dealer"], "Zapdos")
        self.assertEqual(turn1_damage_event["Dealer_Player_Number"], 1)
        self.assertEqual(turn1_damage_event["Receiver"], "Gardevoir")
        self.assertEqual(turn1_damage_event["Receiver_Player_Number"], 2)
        self.assertEqual(turn1_damage_event["Type"], "move")


if __name__ == "__main__":
    unittest.main()
