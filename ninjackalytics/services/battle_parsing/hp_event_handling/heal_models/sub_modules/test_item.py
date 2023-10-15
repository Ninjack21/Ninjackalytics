import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import ItemHealData


# =================== useful functions for testing ===================


class TestItemHealData(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        item_turn = MockTurn(
            1,
            """
            |-heal|p2a: Bisharp|100/100|[from] item: Leftovers
            |upkeep
            """,
        )

        self.item_turn = item_turn

        self.data_finder = ItemHealData(mock_battle_pokemon)

    def test_get_heal_data_item(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p2a: Bisharp", 50)
        event = "|-heal|p2a: Bisharp|100/100|[from] item: Leftovers"
        heal_data = self.data_finder.get_heal_data(event, self.item_turn)
        self.assertEqual(heal_data["Healing"], 50)
        self.assertEqual(heal_data["Receiver"], "Bisharp")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Leftovers")
        self.assertEqual(heal_data["Turn"], 1)
        self.assertEqual(heal_data["Type"], "Item")


if __name__ == "__main__":
    unittest.main()
