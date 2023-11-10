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

        turn = MockTurn(
            1,
            """
            |move|p2a: Gardevoir|Psyshock|p1a: Melmetal
            |-resisted|p1a: Melmetal
            |-damage|p1a: Melmetal|83/100
            """,
        )

        event = "|-damage|p1a: Melmetal|83/100"

        # now test the top level code implementation
        (pnum, dealer), source = self.move_dealer_finder.get_dealer_and_source(
            event, turn, MockBattle()
        )
        self.assertEqual(pnum, 2)
        self.assertEqual(dealer, "Gardevoir")
        self.assertEqual(source, "Psyshock")

    def test_phantom_force_case(self):
        # test case found from: https://replay.pokemonshowdown.com/gen9ou-1985223214.log
        # phantom force
        phantom_force_turn = MockTurn(
            1,
            """
            |turn|27
            |
            |t:|1699351517
            |move|p2a: Dragapult|Phantom Force|p1a: Silver Fox|[from]lockedmove
            |-damage|p1a: Silver Fox|20/100 tox
            |move|p1a: Silver Fox|Aurora Veil|p1a: Silver Fox
            |-sidestart|p1: OUVT Tgirl|move: Aurora Veil
            |
            |-weather|Snow|[upkeep]
            |-heal|p2a: Dragapult|63/100|[from] item: Leftovers
            |-damage|p1a: Silver Fox|8/100 tox|[from] psn
            |upkeep
            """,
        )
        # (dealer, source)
        expected_output = ((2, "Dragapult"), "Phantom Force")
        self.assertEqual(
            self.move_dealer_finder._get_normal_dealer_and_source(
                event="|-damage|p1a: Silver Fox|20/100 tox",
                turn=phantom_force_turn,
            ),
            expected_output,
        )

    def test_ghost_type_curse_dmg(self):
        turn = MockTurn(
            1,
            """
            |turn|7
            |
            |t:|1699522673
            |move|p1a: Dragapult|Curse|p2a: Ursaluna
            |-start|p2a: Ursaluna|Curse|[of] p1a: Dragapult
            |-damage|p1a: Dragapult|0 fnt
            |faint|p1a: Dragapult
            |move|p2a: Ursaluna|Earthquake|p1: Dragapult|[notarget]
            |-fail|p2a: Ursaluna
            |
            |-damage|p2a: Ursaluna|22/100|[from] Curse
            |upkeep
            |
            |t:|1699522682
            |switch|p1a: Moltres|Moltres-Galar|100/100
            """,
        )

        # (dealer, source)
        expected_output = ((1, "Dragapult"), "Curse")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Dragapult|0 fnt",
                turn=turn,
                battle=MockBattle(),
            ),
            expected_output,
        )

    def test_fine_tune_ghost_type_curse_logic(self):
        # https://replay.pokemonshowdown.com/gen9ou-1986255297.log
        # we need to be more specific because abilities like Cursed Body exist, which currently trigger the
        # ghost type curse logic, which we do not want

        turn = MockTurn(
            1,
            """
            |turn|5
            |
            |t:|1699463859
            |move|p2a: Gliscor|Scale Shot|p1a: Dragapult
            |-supereffective|p1a: Dragapult
            |-damage|p1a: Dragapult|29/100
            |-start|p2a: Gliscor|Disable|Scale Shot|[from] ability: Cursed Body|[of] p1a: Dragapult
            |-supereffective|p1a: Dragapult
            |-damage|p1a: Dragapult|0 fnt
            |faint|p1a: Dragapult
            |-hitcount|p1: Dragapult|2
            |-unboost|p2a: Gliscor|def|1
            |-boost|p2a: Gliscor|spe|1
            |
            |upkeep
            |
            |t:|1699463862
            |switch|p1a: Enamorus|Enamorus, F|100/100
            """,
        )

        # (dealer, source)
        expected_output = ((2, "Gliscor"), "Scale Shot")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p1a: Dragapult|0 fnt",
                turn=turn,
                battle=MockBattle(),
            ),
            expected_output,
        )

    def test_event_text_duplicated_within_same_turn(self):
        # https://replay.pokemonshowdown.com/gen8doublesou-1978226780
        """
        due to Mimikyu's disguise the line: |-damage|p2a: Mimikyu|91/100 shows up in two places! This causes the
        pre-event test to be incorrect as it is using the first instance, which in this case, is the one furthest
        away and at the beginning of the battle.
        """
        turn = MockTurn(
            1,
            """
            |turn|9
            |
            |t:|1698514849
            |move|p2a: Mimikyu|Play Rough|p1a: Incineroar
            |-damage|p1a: Incineroar|1/100
            |-damage|p2a: Mimikyu|91/100|[from] item: Life Orb
            |move|p2b: Alcremie|Decorate|p2a: Mimikyu
            |-boost|p2a: Mimikyu|atk|2
            |-boost|p2a: Mimikyu|spa|2
            |move|p1a: Incineroar|Knock Off|p2a: Mimikyu
            |-activate|p2a: Mimikyu|ability: Disguise
            |-damage|p2a: Mimikyu|91/100
            |-enditem|p2a: Mimikyu|Life Orb|[from] move: Knock Off|[of] p1a: Incineroar
            |detailschange|p2a: Mimikyu|Mimikyu-Busted, F
            |-damage|p2a: Mimikyu|78/100|[from] pokemon: Mimikyu-Busted
            |move|p1b: Perrserker|Iron Head|p2a: Mimikyu
            |-supereffective|p2a: Mimikyu
            |-damage|p2a: Mimikyu|0 fnt
            |faint|p2a: Mimikyu
            |
            |-weather|none
            |upkeep
            """,
        )

        # (dealer, source)
        expected_output = ((1, "Incineroar"), "Knock Off")
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p2a: Mimikyu|91/100",
                turn=turn,
                battle=MockBattle(),
            ),
            expected_output,
        )

    def test_metronome_curse(self):
        """
        Need to figure out why this failed but at first glance, it seems to be a weird combination of metronome
        into Curse so that may be causing issues. May not be worth solving just because of how rare this probably
        is.
        """

        turn = MockTurn(
            1,
            """
            |turn|13
            |
            |t:|1698967337
            |move|p2a: Milk Roll|Metronome|p2a: Milk Roll
            |move|p2a: Milk Roll|Trick-or-Treat|p1a: Egg-Coat|[from]move: Metronome
            |-start|p1a: Egg-Coat|typeadd|Ghost|[from] move: Trick-or-Treat
            |move|p1a: Egg-Coat|Metronome|p1a: Egg-Coat
            |move|p1a: Egg-Coat|Curse|p2a: Milk Roll|[from]move: Metronome
            |-start|p2a: Milk Roll|Curse|[of] p1a: Egg-Coat
            |-damage|p1a: Egg-Coat|2/100
            |-activate|p2b: Egg|confusion
            |move|p2b: Egg|Metronome|p2b: Egg
            |move|p2b: Egg|Ice Shard|p1a: Egg-Coat|[from]move: Metronome
            |-damage|p1a: Egg-Coat|0 fnt
            |faint|p1a: Egg-Coat
            """,
        )
        event = "|-damage|p1a: Egg-Coat|2/100"
        # (dealer, source)
        expected_output = ((1, "Egg-Coat"), "Curse")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
            ),
            expected_output,
        )


if __name__ == "__main__":
    unittest.main()
