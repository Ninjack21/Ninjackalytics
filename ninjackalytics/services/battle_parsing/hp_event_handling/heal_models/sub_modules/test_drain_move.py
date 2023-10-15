import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import DrainMoveHealData


class TestDrainMoveHealData(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        drain_turn = MockTurn(
            15,
            """
            |move|p2a: Torkoal|Should Not Be Me|p1a: Abomasnow
            |move|p1a: Abomasnow|Giga Drain|p2a: Torkoal
            |-damage|p2a: Torkoal|60/100
            |-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal
            |upkeep
            """,
        )

        self.drain_turn = drain_turn

        self.data_finder = DrainMoveHealData(mock_battle_pokemon)

    def test_get_heal_data_drain(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p1a: Abomasnow", 50)
        event = "|-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal"
        heal_data = self.data_finder.get_heal_data(event, self.drain_turn)
        self.assertAlmostEqual(heal_data["Healing"], 8)
        self.assertEqual(heal_data["Receiver"], "Abomasnow")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Giga Drain")
        self.assertEqual(heal_data["Turn"], 15)
        self.assertEqual(heal_data["Type"], "Drain Move")


if __name__ == "__main__":
    unittest.main()
