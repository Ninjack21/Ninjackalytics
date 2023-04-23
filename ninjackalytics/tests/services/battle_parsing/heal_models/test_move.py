import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.heal_models.move import MoveHealData, Turn


# =================== MOCK PROTOCOLS FOR TESTING ===================
# based on protocol in models
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
        if not raw_name in self.mon_hps:
            self.mon_hps[raw_name] = 0
        current_hp = self.mon_hps[raw_name]
        self.mon_hp_changes[raw_name] = new_hp - current_hp
        self.mon_hps[raw_name] = new_hp
        print(
            f"updated hp for {raw_name} to {new_hp} (change: {self.mon_hp_changes[raw_name]}"
        )

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        return self.mon_hps[raw_name]


mock_battle_pokemon = MockBattlePokemon()


class MockBattle:
    def __init__(self):
        turns = []

    # quick implementation for testing
    def get_turns(self) -> list:
        return self.turns


mock_battle = MockBattle()

# =================== MOCK PROTOCOLS FOR TESTING ===================


# =================== useful functions for testing ===================
def strip_leading_spaces(text: str) -> str:
    return "\n".join(line.lstrip() for line in text.strip().split("\n"))


# =================== useful functions for testing ===================


class TestMoveHealData(unittest.TestCase):
    def setUp(self):
        move_turn = Mock(Turn)
        move_turn.number = 22
        move_turn.text = """
            |move|p2a: Moltres|Roost|p2a: Moltres
            |-heal|p2a: Moltres|96/100
            |upkeep
            """
        move_turn.textt = strip_leading_spaces(move_turn.text)

        self.move_turn = move_turn

        wish_turn = Mock(Turn)
        wish_turn.number = 26
        wish_turn.text = """
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
            """

        wish_turn.text = strip_leading_spaces(wish_turn.text)
        self.wish_turn = wish_turn

        self.mock_battle = mock_battle
        self.mock_battle.turns = [move_turn, wish_turn]

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
