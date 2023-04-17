import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models.d_type_specific_models import (
    MoveDataFinder,
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
        self.mon_hp_changes[raw_name] = current_hp - new_hp
        self.mon_hps[raw_name] = new_hp

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        if not raw_name in self.mon_hps:
            self.mon_hps[raw_name] = 100.0
        return self.mon_hps[raw_name]


mock_battle_pokemon = MockBattlePokemon()


class MockBattle:
    def __init__(self):
        turns = []

    # quick implementation for testing
    def get_turns(self) -> list:
        return self.turns


mock_battle = MockBattle()


class MockTurn:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


# =================== useful functions for testing ===================
def strip_leading_spaces(text: str) -> str:
    return "\n".join(line.lstrip() for line in text.strip().split("\n"))


# =================== UnitTests ===================


class TestMoveDataFinder(unittest.TestCase):
    def setUp(self):
        self.move_data_finder = MoveDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # move types tested in DealerSourceFinder already, just check other parts
        normal_turn = MockTurn(
            1,
            strip_leading_spaces(
                """
            |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
            |-damage|p1a: Cuss-Tran|67/100
            """
            ),
        )

        event = "|-damage|p1a: Cuss-Tran|67/100"
        mock_battle.turns = [normal_turn]

        damage_data = self.move_data_finder.get_damage_data(
            event, normal_turn, mock_battle
        )

        self.assertEqual(damage_data["Type"], "move")
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
