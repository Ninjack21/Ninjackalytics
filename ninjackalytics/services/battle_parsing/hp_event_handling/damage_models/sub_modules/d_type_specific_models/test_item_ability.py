import unittest
from unittest.mock import Mock

from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules.d_type_specific_models import (
    ItemAbilityDataFinder,
)

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import (
    MockBattle,
    MockBattlePokemon,
    MockTurn,
)


class TestItemAbilityDataFinder(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        self.item_or_ability_data_finder = ItemAbilityDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test case 1
        event1 = "|-damage|p2a: BrainCell|372/424|[from] item: Life Orb"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Life Orb",
            "Dealer_Player_Number": 2,
            "Receiver": "BrainCell",
            "Receiver_Player_Number": 2,
            "Source_Name": "Life Orb",
            "Damage": (52 / 424) * 100,
            "Type": "Item",
            "Turn": 1,
        }
        actual_output1 = self.item_or_ability_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test case 2
        event2 = "|-damage|p1a: Pikachu|120/169|[from] ability: Static"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "Static",
            "Dealer_Player_Number": 1,
            "Receiver": "Pikachu",
            "Receiver_Player_Number": 1,
            "Source_Name": "Static",
            "Damage": (49 / 169) * 100,
            "Type": "Ability",
            "Turn": 5,
        }
        actual_output2 = self.item_or_ability_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 3 - event without item or ability damage
        with self.assertRaises(ValueError):
            event3 = "|-damage|p1a: Pikachu|120/169"
            turn3 = MockTurn(5, event3)
            self.item_or_ability_data_finder.get_damage_data(event3, turn3)

    def test_get_rocky_helmet_damages(self):
        """
        We ran into a bug where a Rocky Helmet event was not being recognized as an item event.
        """
        event = "|-damage|p1a: Melmetal|67/100|[from] item: Rocky Helmet|[of] p2a: Gardevoir"
        turn = MockTurn(1, event)

        expected_output = {
            "Dealer": "Gardevoir",
            "Dealer_Player_Number": 2,
            "Receiver": "Melmetal",
            "Receiver_Player_Number": 1,
            "Source_Name": "Rocky Helmet",
            "Damage": 33.0,
            "Type": "Item",
            "Turn": 1,
        }
        actual_output = self.item_or_ability_data_finder.get_damage_data(event, turn)

        self.assertEqual(
            actual_output,
            expected_output,
        )


if __name__ == "__main__":
    unittest.main()
