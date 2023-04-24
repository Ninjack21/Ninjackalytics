import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damages import DamageData


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
            self.mon_hps[raw_name] = 100.0

        current_hp = self.mon_hps[raw_name]
        self.mon_hp_changes[raw_name] = new_hp - current_hp
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


# =================== MOCK PROTOCOLS FOR TESTING ===================


# =================== useful functions for testing ===================
def strip_leading_spaces(text: str) -> str:
    return "\n".join(line.lstrip() for line in text.strip().split("\n"))


class TestDamageData(unittest.TestCase):
    def setUp(self):
        self.damage_data = DamageData(mock_battle, mock_battle_pokemon)

    def test_get_move_data(self):
        move_turn = MockTurn(
            1,
            strip_leading_spaces(
                """
                |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
                |-damage|p1a: Cuss-Tran|67/100
                """
            ),
        )

        event = "|-damage|p1a: Cuss-Tran|67/100"

        move_data = self.damage_data.get_damage_data(event, move_turn)

        self.assertEqual(move_data["Damage"], 33)
        self.assertEqual(move_data["Dealer"], "Blissey")
        self.assertEqual(move_data["Dealer_Player_Number"], 2)
        self.assertEqual(move_data["Source_Name"], "Seismic Toss")
        self.assertEqual(move_data["Receiver"], "Cuss-Tran")
        self.assertEqual(move_data["Receiver_Player_Number"], 1)
        self.assertEqual(move_data["Turn"], 1)
        self.assertEqual(move_data["Type"], "Move")

    def test_get_item_data(self):
        event = "|-damage|p2a: BrainCell|50/100|[from] item: Life Orb"
        turn = MockTurn(1, event)

        item_data = self.damage_data.get_damage_data(event, turn)

        self.assertEqual(item_data["Damage"], 50)
        self.assertEqual(item_data["Dealer"], "Life Orb")
        self.assertEqual(item_data["Dealer_Player_Number"], 2)
        self.assertEqual(item_data["Source_Name"], "Life Orb")
        self.assertEqual(item_data["Receiver"], "BrainCell")
        self.assertEqual(item_data["Receiver_Player_Number"], 2)
        self.assertEqual(item_data["Turn"], 1)
        self.assertEqual(item_data["Type"], "Item")

    def test_get_ability_data(self):
        event = "|-damage|p1a: Pikachu|80/100|[from] ability: Static"
        turn = MockTurn(1, event)

        move_data = self.damage_data.get_damage_data(event, turn)

        self.assertEqual(move_data["Damage"], 20)
        self.assertEqual(move_data["Dealer"], "Static")
        self.assertEqual(move_data["Dealer_Player_Number"], 1)
        self.assertEqual(move_data["Source_Name"], "Static")
        self.assertEqual(move_data["Receiver"], "Pikachu")
        self.assertEqual(move_data["Receiver_Player_Number"], 1)
        self.assertEqual(move_data["Turn"], 1)
        self.assertEqual(move_data["Type"], "Ability")

    def test_get_hazard_data(self):
        event = "|-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock"
        turn = MockTurn(1, event)

        dmg_data = self.damage_data.get_damage_data(event, turn)

        self.assertEqual(dmg_data["Damage"], 6)
        self.assertEqual(dmg_data["Dealer"], "Stealth Rock")
        self.assertEqual(dmg_data["Dealer_Player_Number"], 1)
        self.assertEqual(dmg_data["Source_Name"], "Stealth Rock")
        self.assertEqual(dmg_data["Receiver"], "Ferrothorn")
        self.assertEqual(dmg_data["Receiver_Player_Number"], 2)
        self.assertEqual(dmg_data["Turn"], 1)
        self.assertEqual(dmg_data["Type"], "Hazard")

    def test_get_status_data(self):
        event = "|-damage|p1a: Rillaboom|94/100 tox|[from] psn"
        turn = MockTurn(1, event)

        move_data = self.damage_data.get_damage_data(event, turn)

        self.assertEqual(move_data["Damage"], 6)
        self.assertEqual(move_data["Dealer"], "tox")
        self.assertEqual(move_data["Dealer_Player_Number"], 2)
        self.assertEqual(move_data["Source_Name"], "tox")
        self.assertEqual(move_data["Receiver"], "Rillaboom")
        self.assertEqual(move_data["Receiver_Player_Number"], 1)
        self.assertEqual(move_data["Turn"], 1)
        self.assertEqual(move_data["Type"], "Status")

    def test_get_passive_data(self):
        event = "|-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn"
        turn = MockTurn(1, event)

        move_data = self.damage_data.get_damage_data(event, turn)

        self.assertEqual(move_data["Damage"], 12)
        self.assertEqual(move_data["Dealer"], "Ferrothorn")
        self.assertEqual(move_data["Dealer_Player_Number"], 2)
        self.assertEqual(move_data["Source_Name"], "Leech Seed")
        self.assertEqual(move_data["Receiver"], "Druddigon")
        self.assertEqual(move_data["Receiver_Player_Number"], 1)
        self.assertEqual(move_data["Turn"], 1)
        self.assertEqual(move_data["Type"], "Passive")

    def test_get_all_damage_data(self):
        turn1 = MockTurn(
            1,
            strip_leading_spaces(
                """
                |move|p2a: Blissey|Seismic Toss|p1a: Heatran
                |-damage|p1a: Heatran|67/100
                """
            ),
        )

        turn2 = MockTurn(
            2,
            strip_leading_spaces(
                """
                |-damage|p1a: Raichu|80/100|[from] ability: Static
                """
            ),
        )

        self.damage_data.battle.turns = [turn1, turn2]

        all_damage_data = self.damage_data.get_all_damage_data()

        # Assert the first event
        first_event = all_damage_data[0]
        self.assertEqual(first_event["Damage"], 33)
        self.assertEqual(first_event["Dealer"], "Blissey")
        self.assertEqual(first_event["Dealer_Player_Number"], 2)
        self.assertEqual(first_event["Source_Name"], "Seismic Toss")
        self.assertEqual(first_event["Receiver"], "Heatran")
        self.assertEqual(first_event["Receiver_Player_Number"], 1)
        self.assertEqual(first_event["Turn"], 1)
        self.assertEqual(first_event["Type"], "Move")

        # Assert the second event
        second_event = all_damage_data[1]
        self.assertEqual(second_event["Damage"], 20)
        self.assertEqual(second_event["Dealer"], "Static")
        self.assertEqual(second_event["Dealer_Player_Number"], 1)
        self.assertEqual(second_event["Source_Name"], "Static")
        self.assertEqual(second_event["Receiver"], "Raichu")
        self.assertEqual(second_event["Receiver_Player_Number"], 1)
        self.assertEqual(second_event["Turn"], 2)
        self.assertEqual(second_event["Type"], "Ability")


if __name__ == "__main__":
    unittest.main()
