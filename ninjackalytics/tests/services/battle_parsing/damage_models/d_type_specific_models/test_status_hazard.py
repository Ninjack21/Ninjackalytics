import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models.d_type_specific_models import (
    StatusHazardDataFinder,
)


# =================== MOCK PROTOCOLS FOR TESTING ===================
# based on protocol
class MockBattlePokemon:
    def __init__(self):
        self.mon_hps = {}
        self.mon_hp_changes = {}

    # quick implementation for testing
    def get_pnum_and_name(self, raw_name):
        """
        example raw_name = 'p1a: May Day Parade'
        """
        pnum_split_name = raw_name.split(": ")
        pnum = int(pnum_split_name[0][1])
        name = pnum_split_name[1]
        return pnum, name

        self.mock_battle_pokemon = MockBattlePokemon()

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        # assumes not called before get_current_hp, which inits mon_hps
        current_hp = self.mon_hps[raw_name]
        self.mon_hp_changes[raw_name] = new_hp - current_hp
        self.mon_hps[raw_name] = new_hp

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        if not raw_name in self.mon_hps:
            self.mon_hps[raw_name] = 100.0
        return self.mon_hps[raw_name]


mock_battle_pokemon = MockBattlePokemon()


class MockTurn:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


# =================== MOCK PROTOCOLS FOR TESTING ===================


class TestStatusHazardDataFinder(unittest.TestCase):
    def setUp(self):
        self.status_hazard_data_finder = StatusHazardDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test hazard damage
        event1 = "|-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Stealth Rock",
            "Dealer_Player_Number": 1,
            "Receiver": "Ferrothorn",
            "Receiver_Player_Number": 2,
            "Source_Name": "Stealth Rock",
            "Damage": (6 / 100) * 100,
            "Type": "Hazard",
            "Turn": 1,
        }
        actual_output1 = self.status_hazard_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test toxic damage
        event2 = "|-damage|p1a: Rillaboom|94/100 tox|[from] psn"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "tox",
            "Dealer_Player_Number": 2,
            "Receiver": "Rillaboom",
            "Receiver_Player_Number": 1,
            "Source_Name": "tox",
            "Damage": (6 / 100) * 100,
            "Type": "Status",
            "Turn": 5,
        }
        actual_output2 = self.status_hazard_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test normal poison damage
        event2 = "|-damage|p1a: Jigglypuff|94/100|[from] psn"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "psn",
            "Dealer_Player_Number": 2,
            "Receiver": "Jigglypuff",
            "Receiver_Player_Number": 1,
            "Source_Name": "psn",
            "Damage": (6 / 100) * 100,
            "Type": "Status",
            "Turn": 5,
        }
        actual_output2 = self.status_hazard_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 4 - event without status or hazard
        with self.assertRaises(ValueError):
            event3 = "|-damage|p1a: Pikachu|120/169"
            turn3 = MockTurn(5, event3)
            self.status_hazard_data_finder.get_damage_data(event3, turn3)


if __name__ == "__main__":
    unittest.main()
