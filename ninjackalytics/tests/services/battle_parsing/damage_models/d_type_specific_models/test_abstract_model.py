import unittest
from unittest.mock import Mock
from typing import Dict, Tuple, List, Protocol

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models.d_type_specific_models.abstract_model import (
    DamageDataFinder,
    BattlePokemon,
    Turn,
    Battle,
)


class MockBattlePokemon(BattlePokemon):
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
        self.mon_hp_changes[raw_name] = new_hp - current_hp
        self.mon_hps[raw_name] = new_hp

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        if not raw_name in self.mon_hps:
            self.mon_hps[raw_name] = 100.0
        return self.mon_hps[raw_name]


class MockTurn(Turn):
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


class MockBattle(Battle):
    def __init__(self, turns: List[Turn]):
        self.turns = turns

    def get_turns(self) -> List[Turn]:
        return self.turns


class MockDamageDataFinder(DamageDataFinder):
    def get_damage_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        return {}

    def _get_source_name(self, event: str) -> str:
        return "Source"


class MockDamageDataFinder(DamageDataFinder):
    def get_damage_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        return {}

    def _get_source_name(self, event: str) -> str:
        return "Source"


class TestDamageDataFinder(unittest.TestCase):
    def setUp(self):
        self.battle_pokemon = MockBattlePokemon()
        self.damage_data_finder = MockDamageDataFinder(self.battle_pokemon)

    def test_get_receiver(self):
        event = "|-damage|p2a: Zapdos|57/100."
        pnum, raw_name = self.damage_data_finder._get_receiver(event)
        self.assertEqual(pnum, 2)
        self.assertEqual(raw_name, "Zapdos")

    def test_get_hp_change(self):
        event = "|-damage|p1a: pikachu|80/100"
        receiver = "p1a: pikachu"
        expected_hp_change = 20
        actual_hp_change = self.damage_data_finder._get_hp_change(event, receiver)
        self.assertEqual(actual_hp_change, expected_hp_change)

        event = "|-damage|p2a: BrainCell|70/100|[from] item: Life Orb"
        receiver = "p2a: BrainCell"
        expected_hp_change = 30
        actual_hp_change = self.damage_data_finder._get_hp_change(event, receiver)
        self.assertAlmostEqual(actual_hp_change, expected_hp_change, places=2)

    def test_get_hp_change_if_faint(self):
        """
        Ran into issue where if "0 fnt" is in the hp it fails because cannot divide since no
        more "/" in the string

        original error:
        new_hp = float(new_raw_hp[0]) / float(new_raw_hp[1].split(" ")[0]) * 100
             ^^^^^^^^^^^^^^^^^^^^
        ValueError: could not convert string to float: '0 fnt'

        event: |-damage|p2a: Gardevoir|0 fnt
        """
        event = "|-damage|p2a: Gardevoir|0 fnt"
        receiver = "p2a: Gardevoir"

        expected_hp_change = 100
        actual_hp_change = self.damage_data_finder._get_hp_change(event, receiver)
        self.assertEqual(actual_hp_change, expected_hp_change)


if __name__ == "__main__":
    unittest.main()
