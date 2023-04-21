import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models import (
    ReceiverFinder,
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


# =================== MOCK PROTOCOLS FOR TESTING ===================


class TestReceiverFinder(unittest.TestCase):
    def setUp(self):
        self.receiver_finder = ReceiverFinder(mock_battle_pokemon)

    def test_get_receiver(self):
        # Define some test cases
        test_cases = [
            ("|-damage|p1a: Blissey|67/100", (1, "Blissey")),
            ("|-damage|p2a: Incineroar|67/100", (2, "Incineroar")),
            ("|-damage|p1a: Cuss-Tran|67/100", (1, "Cuss-Tran")),
        ]

        for event, expected_output in test_cases:
            self.assertEqual(
                self.receiver_finder.get_receiver(event),
                expected_output,
            )


if __name__ == "__main__":
    unittest.main()
