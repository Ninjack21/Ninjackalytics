import unittest
from unittest.mock import Mock

from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules.d_type_specific_models import (
    MoveDataFinder,
)

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import (
    MockBattle,
    MockBattlePokemon,
    MockTurn,
)

# =================== UnitTests ===================


class TestMoveDataFinder(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        self.move_data_finder = MoveDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # move types tested in DealerSourceFinder already, just check other parts
        normal_turn = MockTurn(
            1,
            """
            |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
            |-damage|p1a: Cuss-Tran|67/100
            """,
        )

        event = "|-damage|p1a: Cuss-Tran|67/100"
        mock_battle = MockBattle()
        mock_battle.turns = [normal_turn]

        damage_data = self.move_data_finder.get_damage_data(
            event, normal_turn, mock_battle
        )

        self.assertEqual(damage_data["Type"], "Move")
        self.assertEqual(damage_data["Dealer"], "Blissey")
        self.assertEqual(damage_data["Dealer_Player_Number"], 2)
        self.assertEqual(damage_data["Source_Name"], "Seismic Toss")
        self.assertEqual(damage_data["Damage"], 33.0)
        self.assertEqual(damage_data["Receiver"], "Cuss-Tran")
        self.assertEqual(damage_data["Receiver_Player_Number"], 1)
        self.assertEqual(damage_data["Turn"], 1)

        # test bad input
        bad_turn = MockTurn(2, "|-damage|p1a: Cuss-Tran|67/100| [from] non-move")
        bad_event = "|-damage|p1a: Cuss-Tran|67/100| [from] non-move"
        mock_battle.turns = [bad_turn]

        with self.assertRaises(ValueError):
            damage_data = self.move_data_finder.get_damage_data(
                bad_event, bad_turn, mock_battle
            )


if __name__ == "__main__":
    unittest.main()
