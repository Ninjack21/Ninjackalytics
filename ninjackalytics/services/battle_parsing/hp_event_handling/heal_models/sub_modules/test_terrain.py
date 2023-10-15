import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import TerrainHealData


class TestTerrainHealData(unittest.TestCase):
    def setUp(self):
        terrain_turn = MockTurn(
            4,
            """
            |-heal|p2a: Tyranitar|91/100|[from] Grassy Terrain
            |upkeep
            """,
        )

        self.terrain_turn = terrain_turn
        mock_battle_pokemon = MockBattlePokemon()

        self.data_finder = TerrainHealData(mock_battle_pokemon)

    def test_get_heal_data_terrain(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p2a: Tyranitar", 50)
        event = "|-heal|p2a: Tyranitar|91/100|[from] Grassy Terrain"
        heal_data = self.data_finder.get_heal_data(event, self.terrain_turn)
        self.assertEqual(heal_data["Healing"], 41)
        self.assertEqual(heal_data["Receiver"], "Tyranitar")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Grassy Terrain")
        self.assertEqual(heal_data["Turn"], 4)
        self.assertEqual(heal_data["Type"], "Terrain")


if __name__ == "__main__":
    unittest.main()
