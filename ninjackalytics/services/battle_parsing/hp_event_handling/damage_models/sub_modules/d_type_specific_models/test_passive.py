import unittest
from unittest.mock import Mock

from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules.d_type_specific_models import (
    PassiveDataFinder,
)

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import (
    MockBattle,
    MockBattlePokemon,
    MockTurn,
)


# =================== MOCK PROTOCOLS FOR TESTING ===================
class TestPassiveDataFinder(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        self.passive_data_finder = PassiveDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test passive damage with obvious dealer
        event1 = "|-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Ferrothorn",
            "Dealer_Player_Number": 2,
            "Receiver": "Druddigon",
            "Receiver_Player_Number": 1,
            "Source_Name": "Leech Seed",
            "Damage": (12 / 100) * 100,
            "Type": "Passive",
            "Turn": 1,
        }
        actual_output1 = self.passive_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test passive damage without [of]
        # NOTE: as seen in code, I do not currently know of case where this exists
        event2 = "|-damage|p1a: Aggron|88/100|[from] something weird"
        turn1 = MockTurn(1, event2)

        expected_output2 = {
            "Dealer": "something weird",
            "Dealer_Player_Number": 2,
            "Receiver": "Aggron",
            "Receiver_Player_Number": 1,
            "Source_Name": "something weird",
            "Damage": (12 / 100) * 100,
            "Type": "Passive",
            "Turn": 1,
        }
        actual_output2 = self.passive_data_finder.get_damage_data(event2, turn1)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 3 - weather damage
        event3 = "|-damage|p1a: Seismitoad|6/100|[from] Hail"
        turn3 = MockTurn(5, event3)

        expected_output3 = {
            "Dealer": "Hail",
            "Dealer_Player_Number": 2,
            "Receiver": "Seismitoad",
            "Receiver_Player_Number": 1,
            "Source_Name": "Hail",
            "Damage": (94 / 100) * 100,
            "Type": "Passive",
            "Turn": 5,
        }
        actual_output3 = self.passive_data_finder.get_damage_data(event3, turn3)
        # round to 2 decimal places
        expected_output3["Damage"] = round(expected_output3["Damage"], 2)
        actual_output3["Damage"] = round(actual_output3["Damage"], 2)

        self.assertEqual(
            actual_output3,
            expected_output3,
        )

        # Test case 4 - no [from] found (would normally indidcate a move damage)
        with self.assertRaises(ValueError):
            event3 = "|-damage|p2a: Ferrothorn|94/100|"
            turn3 = MockTurn(5, event3)
            self.passive_data_finder.get_damage_data(event3, turn3)


if __name__ == "__main__":
    unittest.main()
