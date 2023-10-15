import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattle, MockBattlePokemon, MockTurn

# ===bring in object to test===
from .dealer_source_finder import DealerSourceFinder


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
            """
            |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
            |-damage|p1a: Cuss-Tran|67/100
            """,
        )

        delayed_turn = MockTurn(
            1,
            """
            |-end|p1a: Ninetales|move: Future Sight
            |-damage|p1a: Ninetales|44/100
            """,
        )

        doubles_turn1 = MockTurn(
            3,
            """
            |move|p2a: Genesect|Techno Blast|p1a: Palossand
            |-damage|p1a: Palossand|65/100
            """,
        )

        doubles_turn2 = MockTurn(
            4,
            """
                |move|p1a: Palossand|Scorching Sands|p2b: Incineroar
                |-damage|p2b: Incineroar|76/100
                """,
        )

        doubles_anim_turn = MockTurn(
            5,
            """
                |-anim||move|p1b: Dragapult|Dragon Darts|p2a: Pelipper
                |-damage|p2a: Pelipper|65/100
                |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
                |-damage|p2b: Incineroar|31/100
                """,
        )

        spread_turn1 = MockTurn(
            6,
            """
                |move|p2a: Regidrago|Dragon Energy|p1b: Regieleki|[spread] p1a,p1b
                |-damage|p1a: Indeedee|15/100
                |-damage|p1b: Regieleki|0 fnt
                """,
        )

        self.normalturn = normal_turn
        self.delayedturn = delayed_turn
        self.doublesturn1 = doubles_turn1
        self.doublesturn2 = doubles_turn2
        self.animatedturn = doubles_anim_turn
        self.spreadturn1 = spread_turn1

        mock_battle_pokemon = MockBattlePokemon()

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

    def test_get_move_type_normal_move(self):
        """
        Not sure how yet, but this scenario failed the DealerSourceFinder. It raised the ValueError I added
        to say that a move type was unable to be determined.
        """

        event = "|-damage|p1a: Melmetal|83/100"
        turn_text = """|move|p2a: Gardevoir|Psyshock|p1a: Melmetal
            |-resisted|p1a: Melmetal
            |-damage|p1a: Melmetal|83/100
            """
        turn = MockTurn(1, turn_text)

        # first, let's check that the move_type is found by the _move_method
        for line in reversed(list(turn_text.split(event)[0].splitlines())):
            move_type = self.move_dealer_finder._get_move_type(line)
            if move_type is not None:
                break

        self.assertEqual(move_type, "normal")

        # now test the top level code implementation
        (pnum, dealer), source = self.move_dealer_finder.get_dealer_and_source(
            event, turn, MockBattle()
        )
        self.assertEqual(pnum, 2)
        self.assertEqual(dealer, "Gardevoir")
        self.assertEqual(source, "Psyshock")


if __name__ == "__main__":
    unittest.main()
