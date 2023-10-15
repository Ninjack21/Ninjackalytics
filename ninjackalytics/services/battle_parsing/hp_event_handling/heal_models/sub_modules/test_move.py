import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn, MockBattle

# ===bring in object to test===
from . import MoveHealData


class TestMoveHealData(unittest.TestCase):
    def setUp(self):
        move_turn = MockTurn(
            22,
            """
            |move|p2a: Moltres|Roost|p2a: Moltres
            |-heal|p2a: Moltres|96/100
            |upkeep
            """,
        )

        self.move_turn = move_turn

        wish_turn = MockTurn(
            26,
            """
            |turn|26
            |
            |t:|1682240385
            |switch|p2a: Seismitoad|Seismitoad, M|71/100
            |-damage|p2a: Seismitoad|65/100|[from] Stealth Rock
            |move|p1a: Bisharp|Swords Dance|p1a: Bisharp
            |-boost|p1a: Bisharp|atk|2
            |
            |-heal|p2a: Seismitoad|100/100|[from] move: Wish|[wisher] Clefable
            |upkeep
            """,
        )

        self.wish_turn = wish_turn

        self.mock_battle = MockBattle()
        self.mock_battle.turns = [move_turn, wish_turn]
        mock_battle_pokemon = MockBattlePokemon()
        self.data_finder = MoveHealData(mock_battle_pokemon)

    def test_get_heal_data_move(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p2a: Moltres", 50)
        event = "|-heal|p2a: Moltres|96/100"
        heal_data = self.data_finder.get_heal_data(
            event, self.move_turn, self.mock_battle
        )
        self.assertEqual(heal_data["Healing"], 46)
        self.assertEqual(heal_data["Receiver"], "Moltres")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Roost")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Move")

    def test_get_heal_data_wish(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p2a: Seismitoad", 50)
        event = "|-heal|p2a: Seismitoad|100/100|[from] move: Wish|[wisher] Clefable"
        heal_data = self.data_finder.get_heal_data(
            event, self.wish_turn, self.mock_battle
        )
        self.assertEqual(heal_data["Healing"], 50)
        self.assertEqual(heal_data["Receiver"], "Seismitoad")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Wish")
        self.assertEqual(heal_data["Turn"], 26)
        self.assertEqual(heal_data["Type"], "Move")


if __name__ == "__main__":
    unittest.main()
