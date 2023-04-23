import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.heal_models.passive import PassiveHealData, Turn


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

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
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


class TestPassiveHealData(unittest.TestCase):
    def setUp(self):
        # leech seed example - can find source by damage immediately preceeding
        # I am not sure that you can do that for all [silent] heals
        passive_turn = Mock(Turn)
        passive_turn.number = 9
        passive_turn.text = """
            |-damage|p2a: Skarmory|25/100|[from] Leech Seed|[of] p1a: Frosmoth
            |-heal|p1a: Frosmoth|82/100 tox|[silent]
            |upkeep
            """
        passive_turn.text = strip_leading_spaces(passive_turn.text)

        self.passive_turn = passive_turn

        self.data_finder = PassiveHealData(mock_battle_pokemon)

    def test_get_heal_data_passive(self):
        event = "|-heal|p1a: Frosmoth|82/100|[from] Leech Seed"
        heal_data = self.data_finder.get_heal_data(event, self.passive_turn)
        self.assertEqual(heal_data["Healing"], 82)
        self.assertEqual(heal_data["Receiver"], "Frosmoth")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Leech Seed")
        self.assertEqual(heal_data["Turn"], 9)
        self.assertEqual(heal_data["Type"], "Passive")


if __name__ == "__main__":
    unittest.main()
