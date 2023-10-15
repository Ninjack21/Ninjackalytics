import unittest
from unittest.mock import Mock

from . import (
    StatusHazardDataFinder,
)

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import (
    MockBattle,
    MockBattlePokemon,
    MockTurn,
)


class TestStatusHazardDataFinder(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
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
