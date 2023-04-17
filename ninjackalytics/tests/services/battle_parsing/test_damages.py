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


# =================== MOCK PROTOCOLS FOR TESTING ===================


# =================== useful functions for testing ===================
def strip_leading_spaces(text: str) -> str:
    return "\n".join(line.lstrip() for line in text.strip().split("\n"))


class TestDamageData(unittest.TestCase):
    def setUp(self):
        self.mock_battle = Mock(spec=Battle)
        self.mock_battle_pokemon = Mock(spec=BattlePokemon)
        self.damage_data = DamageData(self.mock_battle, self.mock_battle_pokemon)

    def test_get_source(self):
        test_cases = [
            {
                "event": "|-damage|p2a: AMagicalFox|213/292",
                "expected_source": "move",
            },
            {
                "event": "|-damage|p2a: AMagicalFox|213/292|[from] item: Life Orb",
                "expected_source": "item",
            },
            {
                "event": "|-damage|p2a: AMagicalFox|213/292|[from] ability: Rough Skin",
                "expected_source": "ability",
            },
            {
                "event": "|-damage|p2a: AMagicalFox|213/292|[from] Stealth Rock",
                "expected_source": "hazard",
            },
            {
                "event": "|-damage|p2a: AMagicalFox|213/292|[from] psn",
                "expected_source": "status",
            },
            {
                "event": "|-damage|p2a: AMagicalFox|213/292|[from] some_unknown_event",
                "expected_source": "passive",
            },
        ]

        for test_case in test_cases:
            event = test_case["event"]
            expected_source = test_case["expected_source"]
            actual_source = self.damage_data.get_source(event)

            self.assertEqual(
                actual_source, expected_source, f"Failed for event: {event}"
            )


if __name__ == "__main__":
    unittest.main()
