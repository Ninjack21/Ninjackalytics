import unittest
from unittest.mock import Mock
from typing import Dict, Tuple, List, Protocol


# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import (
    MockBattle,
    MockBattlePokemon,
    MockTurn,
)


# ===bring in object to test===
from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules.d_type_specific_models.abstract_model import (
    DamageDataFinder,
)


class MockDamageDataFinder(DamageDataFinder):
    def get_damage_data(
        self, event: str, turn: MockTurn, battle: Battle
    ) -> Dict[str, str]:
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

    def test_get_hp_change_if_toxic_in_hp(self):
        """
        We had an issue where if the hp change had "tox" in it, it would fail to convert to float
        """
        event = "|-damage|p2a: Pelipper|82/100 tox|[from] psn"
        receiver = "p2a: Pelipper"

        expected_hp_change = 18
        actual_hp_change = self.damage_data_finder._get_hp_change(event, receiver)
        self.assertEqual(actual_hp_change, expected_hp_change)


if __name__ == "__main__":
    unittest.main()
