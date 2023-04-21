import unittest
from unittest.mock import Mock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models import (
    DealerSourceFinder,
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


class MockTurn:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


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


class TestDealerSourceFinder(unittest.TestCase):
    def setUp(self):
        """
        normal:
        -------
        |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
        |-damage|p1a: Cuss-Tran|67/100
        delayed:
        --------
        |turn|14
        ...
        |move|p2a: Slowking|Future Sight|p1a: Ninetales
        |-start|p2a: Slowking|move: Future Sight
        ...
        |turn|15
        ...
        |turn|16
        ...
        |-end|p1a: Ninetales|move: Future Sight
        |-damage|p1a: Ninetales|44/100
        ...
        |turn|17
        doubles:
        --------
        |move|p2a: Genesect|Techno Blast|p1a: Palossand
        |-damage|p1a: Palossand|65/100
        |move|p1a: Palossand|Scorching Sands|p2b: Incineroar
        |-damage|p2b: Incineroar|76/100
        doubles_anim:
        -------------
        |-anim||move|p1b: Dragapult|Dragon Darts|p2a: Pelipper
        |-damage|p2a: Pelipper|65/100
        |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
        |-damage|p2b: Incineroar|31/100
        spread:
        -------
        |move|p2a: Regidrago|Dragon Energy|p1b: Regieleki|[spread] p1a,p1b
        |-damage|p1a: Indeedee|15/100
        |-damage|p1b: Regieleki|0 fnt
        """
        normal_turn = MockTurn(
            1,
            strip_leading_spaces(
                """
            |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
            |-damage|p1a: Cuss-Tran|67/100
            """
            ),
        )
        delayed_turn = MockTurn(
            17,
            strip_leading_spaces(
                """
                |-end|p1a: Ninetales|move: Future Sight
                |-damage|p1a: Ninetales|44/100
                """
            ),
        )

        doubles_turn1 = MockTurn(
            3,
            strip_leading_spaces(
                """
                |move|p2a: Genesect|Techno Blast|p1a: Palossand
                |-damage|p1a: Palossand|65/100
                """
            ),
        )

        doubles_turn2 = MockTurn(
            4,
            strip_leading_spaces(
                """
                |move|p1a: Palossand|Scorching Sands|p2b: Incineroar
                |-damage|p2b: Incineroar|76/100
                """
            ),
        )

        doubles_anim_turn = MockTurn(
            5,
            strip_leading_spaces(
                """
                |-anim||move|p1b: Dragapult|Dragon Darts|p2a: Pelipper
                |-damage|p2a: Pelipper|65/100
                |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
                |-damage|p2b: Incineroar|31/100
                """
            ),
        )

        spread_turn1 = MockTurn(
            6,
            strip_leading_spaces(
                """
                |move|p2a: Regidrago|Dragon Energy|p1b: Regieleki|[spread] p1a,p1b
                |-damage|p1a: Indeedee|15/100
                |-damage|p1b: Regieleki|0 fnt
                """
            ),
        )
        self.normalturn = normal_turn
        self.delayedturn = delayed_turn
        self.doublesturn1 = doubles_turn1
        self.doublesturn2 = doubles_turn2
        self.animatedturn = doubles_anim_turn
        self.spreadturn1 = spread_turn1
        self.move_dealer_finder = DealerSourceFinder(mock_battle_pokemon)

    def test_get_dealer_and_source(self):
        # first, create a custom battle log with all the damage types we want to test
        # then we will test several turns to confirm that the top level function correctly
        # calls the lower level functions and can handle identifying when to use which

        mock_battle = MockBattle()
        fsight_start_turn = MockTurn(
            14,
            "|move|p2a: Slowking|Future Sight|p1a: Ninetales\n|-start|p2a: Slowking|move: Future Sight",
        )
        fsight_middle_turn = MockTurn(
            15,
            """
            |
            |t:|1680411602
            |switch|p2a: Clefable|Clefable, M|100/100
            |move|p1a: Ninetales|Aurora Veil|p1a: Ninetales
            |-sidestart|p1: rhkp23|move: Aurora Veil
            |
            |-weather|Hail|[upkeep]
            |upkeep
            """,
        )
        fsight_end_turn = self.delayedturn
        mock_battle.turns = [
            fsight_start_turn,
            fsight_middle_turn,
            fsight_end_turn,
            self.normalturn,
            self.doublesturn1,
            self.doublesturn2,
            self.animatedturn,
            self.spreadturn1,
        ]

        # test normal damage
        expected_output = ((2, "Blissey"), "Seismic Toss")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Cuss-Tran|67/100",
                turn=self.normalturn,
                battle=mock_battle,
            ),
            expected_output,
        )

        # test delayed damage
        expected_output = ((2, "Slowking"), "Future Sight")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Ninetales|44/100",
                turn=self.delayedturn,
                battle=mock_battle,
            ),
            expected_output,
        )

        # test doubles damage
        expected_output = ((2, "Genesect"), "Techno Blast")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Palossand|65/100",
                turn=self.doublesturn1,
                battle=mock_battle,
            ),
            expected_output,
        )

        # test animated damage
        expected_output = ((1, "Dragapult"), "Dragon Darts")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p2a: Pelipper|65/100",
                turn=self.animatedturn,
                battle=mock_battle,
            ),
            expected_output,
        )

        # test spread damage
        expected_output = ((2, "Regidrago"), "Dragon Energy")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Indeedee|15/100",
                turn=self.spreadturn1,
                battle=mock_battle,
            ),
            expected_output,
        )

    def test_get_normal_dealer_and_source(self):
        # test expected case
        # (dealer, source)
        expected_output = ((2, "Blissey"), "Seismic Toss")
        self.assertEqual(
            self.move_dealer_finder._get_normal_dealer_and_source(
                event="|-damage|p1a: Cuss-Tran|67/100",
                turn=self.normalturn,
            ),
            expected_output,
        )

        # test bad input case
        bad_turn_text = "a bad turn text"
        with self.assertRaises(ValueError):
            self.move_dealer_finder._get_normal_dealer_and_source(
                event="|-damage|p1a: Cuss-Tran|67/100",
                turn=MockTurn(1, bad_turn_text),
            )

    def test_get_delayed_dealer_and_source(self):
        mock_battle = MockBattle()
        # don't mess with string, white space breaks and turn 14 is key turn
        fsight_start_turn = MockTurn(
            14,
            "|move|p2a: Slowking|Future Sight|p1a: Ninetales\n|-start|p2a: Slowking|move: Future Sight",
        )
        fsight_middle_turn = MockTurn(
            15,
            """
            |
            |t:|1680411602
            |switch|p2a: Clefable|Clefable, M|100/100
            |move|p1a: Ninetales|Aurora Veil|p1a: Ninetales
            |-sidestart|p1: rhkp23|move: Aurora Veil
            |
            |-weather|Hail|[upkeep]
            |upkeep
            """,
        )
        fsight_end_turn = self.delayedturn
        mock_battle.turns = [fsight_start_turn, fsight_middle_turn, fsight_end_turn]

        # test expected case
        # (dealer, source)
        expected_output = ((2, "Slowking"), "Future Sight")
        self.assertEqual(
            self.move_dealer_finder._get_delayed_dealer_and_source(
                event="|-damage|p1a: Ninetales|44/100",
                turn=self.delayedturn,
                battle=mock_battle,
            ),
            expected_output,
        )

        # test no end indicator
        with self.assertRaises(ValueError):
            self.move_dealer_finder._get_delayed_dealer_and_source(
                event="|-damage|p1a: Ninetales|44/100",
                turn=self.normalturn,
                battle=MockBattle(),
            )

    def test_get_animated_dealer_and_source(self):
        # test expected case
        # (dealer, source)
        expected_output = ((1, "Dragapult"), "Dragon Darts")
        self.assertEqual(
            self.move_dealer_finder._get_animated_dealer_and_source(
                event="|-damage|p2b: Incineroar|52/100",
                turn=self.animatedturn,
            ),
            expected_output,
        )

        # test expected case
        # (dealer, source)
        expected_output = ((1, "Dragapult"), "Dragon Darts")
        self.assertEqual(
            self.move_dealer_finder._get_animated_dealer_and_source(
                event="|-damage|p2a: Pelipper|65/100",
                turn=self.animatedturn,
            ),
            expected_output,
        )

        # test bad input case
        bad_turn_text = "a bad turn text"
        with self.assertRaises(ValueError):
            self.move_dealer_finder._get_animated_dealer_and_source(
                event="|-damage|p2b: Incineroar|52/100",
                turn=MockTurn(1, bad_turn_text),
            )

    def test_get_spread_dealer_and_source(self):
        # test first damage event of spread move
        # (dealer, source)
        expected_output = ((2, "Regidrago"), "Dragon Energy")
        self.assertEqual(
            self.move_dealer_finder._get_spread_dealer_and_source(
                event="|-damage|p1a: Indeedee|15/100",
                turn=self.spreadturn1,
            ),
            expected_output,
        )

        # test second damage event of spread move
        # (dealer, source)
        expected_output = ((2, "Regidrago"), "Dragon Energy")
        self.assertEqual(
            self.move_dealer_finder._get_spread_dealer_and_source(
                event="|-damage|p1a: Indeedee|15/100",
                turn=self.spreadturn1,
            ),
            expected_output,
        )

        # test bad input case
        bad_turn_text = "a bad turn text"
        with self.assertRaises(ValueError):
            self.move_dealer_finder._get_spread_dealer_and_source(
                event="|-damage|p1a: Indeedee|15/100",
                turn=MockTurn(1, bad_turn_text),
            )


if __name__ == "__main__":
    unittest.main()
