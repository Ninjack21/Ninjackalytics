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

    def test_event_text_duplicated_within_same_turn_mimikyu_disguise(self):
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

        # error retriggered on https://replay.pokemonshowdown.com/gen8ou-1968758153

        turn = MockTurn(
            1,
            """
            |turn|46
            |inactive|Takenamecat has 240 seconds left.
            |
            |t:|1697462946
            |move|p1a: Mimikyu|Play Rough|p2a: Drapion
            |-damage|p2a: Drapion|50/100
            |-damage|p1a: Mimikyu|56/100|[from] item: Life Orb
            |move|p2a: Drapion|Knock Off|p1a: Mimikyu
            |-activate|p1a: Mimikyu|ability: Disguise
            |-damage|p1a: Mimikyu|56/100
            |-enditem|p1a: Mimikyu|Life Orb|[from] move: Knock Off|[of] p2a: Drapion
            |detailschange|p1a: Mimikyu|Mimikyu-Busted, F
            |-damage|p1a: Mimikyu|44/100|[from] pokemon: Mimikyu-Busted
            |
            |-heal|p2a: Drapion|56/100|[from] item: Black Sludge
            |upkeep
            """,
        )

        # (dealer, source)
        expected_output = ((2, "Drapion"), "Knock Off")
        event = "|-damage|p1a: Mimikyu|56/100"
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
            ),
            expected_output,
        )

        turn = MockTurn(
            1,
            """
            |turn|31
            |
            |t:|1701974411
            |switch|p1a: Mimikyu|Mimikyu, F|100/100
            |-damage|p1a: Mimikyu|88/100|[from] Stealth Rock
            |move|p2a: Thundurus|Volt Switch|p1a: Mimikyu
            |-activate|p1a: Mimikyu|ability: Disguise
            |-damage|p1a: Mimikyu|88/100
            |detailschange|p1a: Mimikyu|Mimikyu-Busted, F
            |-damage|p1a: Mimikyu|76/100|[from] pokemon: Mimikyu-Busted
            |
            |t:|1701974427
            |switch|p2a: Empoleon|Empoleon, M|34/100|[from] Volt Switch
            |
            |-heal|p2a: Empoleon|40/100|[from] item: Leftovers
            |upkeep
            """,
        )

        # error retriggered on https://replay.pokemonshowdown.com/gen9ubers-2006856742
        # (dealer, source)
        expected_output = ((2, "Thundurus"), "Volt Switch")
        event = "|-damage|p1a: Mimikyu|88/100"
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
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

    def test_get_spread_dealer_and_source_dealer_name_fine_tuning(self):
        # https://replay.pokemonshowdown.com/gen8doublesou-1985108364

        turn = MockTurn(
            1,
            """
        |turn|4
        |
        |t:|1699332082
        |switch|p1b: Teacup|Polteageist|100/100
        |move|p1a: Aqua-Punch|Metronome|p1a: Aqua-Punch
        |move|p1a: Aqua-Punch|Air Cutter|p2a: Wade|[from]move: Metronome|[spread] p2a,p2b
        |-damage|p2a: Wade|34/100
        |-damage|p2b: Leaps|49/100
        |move|p2a: Wade|Metronome|p2a: Wade
        |move|p2a: Wade|Smokescreen|p1a: Aqua-Punch|[from]move: Metronome
        |-unboost|p1a: Aqua-Punch|accuracy|1
        |-activate|p2b: Leaps|confusion
        |move|p2b: Leaps|Metronome|p2b: Leaps
        |move|p2b: Leaps|Psycho Cut|p1a: Aqua-Punch|[from]move: Metronome
        |-supereffective|p1a: Aqua-Punch
        |-damage|p1a: Aqua-Punch|20/100
        |
        |-heal|p1a: Aqua-Punch|27/100|[from] Aqua Ring
        |upkeep
        """,
        )

        # (dealer, source)
        expected_output = ((1, "Aqua-Punch"), "Air Cutter")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p2a: Wade|34/100",
                turn=turn,
                battle=MockBattle(),
            ),
            expected_output,
        )
        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event="|-damage|p2b: Leaps|49/100",
                turn=turn,
                battle=MockBattle(),
            ),
            expected_output,
        )

    def test_end_substitute_doesnt_trigger_delayed_move_type(self):
        # https://replay.pokemonshowdown.com/gen8doublesou-1970583028

        turn = MockTurn(
            1,
            """
            |turn|19
            |inactive|edgypunishment has 120 seconds left.
            |
            |t:|1697650709
            |move|p1a: Bisharp|Sucker Punch|p2a: Genesect
            |-damage|p2a: Genesect|0 fnt
            |faint|p2a: Genesect
            |move|p1b: Drapion|Earthquake|p2b: Diancie|[spread] p1a,p2b
            |-supereffective|p2b: Diancie
            |-end|p2b: Diancie|Substitute
            |-supereffective|p1a: Bisharp
            |-damage|p1a: Bisharp|53/100
            |move|p2b: Diancie|Draining Kiss|p1b: Drapion
            |-damage|p1b: Drapion|51/100
            |-heal|p2b: Diancie|90/100 tox|[from] drain|[of] p1b: Drapion
            |-enditem|p1b: Drapion|Air Balloon
            |
            |-heal|p2b: Diancie|96/100 tox|[from] item: Leftovers
            |-damage|p2b: Diancie|66/100 tox|[from] psn
            |upkeep
            |
            |t:|1697650720
            |switch|p2a: Gastrodon|Gastrodon, F|100/100
            """,
        )

        event = "|-damage|p1a: Bisharp|53/100"

        # (dealer, source)
        expected_output = ((1, "Drapion"), "Earthquake")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
            ),
            expected_output,
        )

    def test_handle_zoroark_end_illusion_case(self):
        # https://replay.pokemonshowdown.com/gen9doublesou-1986368662
        """
        The issue we are running into is when |-end|p1a: Zoroark|Illusion shows up this means that the receiver
        of the original damage will not be the same as the one who took damage - thus the code doesn't think any
        of the identified events belong to this case. This will probably be a hyper specific, goofy fix since
        this mon alone does these shenanigans.
        """
        turn = MockTurn(
            1,
            """
            |turn|6
            |
            |t:|1699473213
            |move|p1b: Braviary|Bitter Malice|p2b: Wendell
            |-damage|p2b: Wendell|9/100 tox
            |-unboost|p2b: Wendell|atk|1
            |move|p1a: Braviary|Iron Head|p2a: Nikki
            |-damage|p2a: Nikki|41/100
            |move|p2b: Wendell|Dual Wingbeat|p1b: Braviary
            |-damage|p1b: Braviary|87/100
            |replace|p1b: Zoroark|Zoroark-Hisui, M, shiny
            |-end|p1b: Zoroark|Illusion
            |-damage|p1b: Zoroark|71/100
            |-hitcount|p1b: Zoroark|2
            |move|p2a: Nikki|Coil|p2a: Nikki
            |-boost|p2a: Nikki|atk|1
            |-boost|p2a: Nikki|def|1
            |-boost|p2a: Nikki|accuracy|1
            |
            |-weather|Sandstorm|[upkeep]
            |-damage|p1b: Zoroark|65/100|[from] Sandstorm
            |-damage|p1a: Braviary|51/100 tox|[from] Sandstorm
            |-heal|p1b: Zoroark|71/100|[from] item: Leftovers
            |-damage|p1a: Braviary|33/100 tox|[from] psn
            |-heal|p2b: Wendell|22/100 tox|[from] ability: Poison Heal
            |upkeep
            """,
        )

        event = "|-damage|p1b: Zoroark|71/100"

        # (dealer, source)
        expected_output = ((2, "Wendell"), "Dual Wingbeat")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
            ),
            expected_output,
        )

    def test_delayed_move_where_delayed_move_comes_from_metronome(self):
        # https://replay.pokemonshowdown.com/gen8doublesou-1981280494
        """
        The issue here was that the regex wasn't specific enough and if a delayed move was triggered by metronome
        it would group the dealer and source name together. I'm starting to notice that including optional groups
        for the from's, of's, etc, are becoming a more common pattern for all of the regexes...
        """

        battle = MockBattle()

        turn3 = MockTurn(
            3,
            """
            |turn|3
            |
            |t:|1698879365
            |move|p1a: Wrecker|Metronome|p1a: Wrecker
            |move|p1a: Wrecker|Baton Pass|p1a: Wrecker|[from]move: Metronome
            |
            |t:|1698879371
            |switch|p1a: Fisterman|Hitmonchan, M|100/100|[from] Baton Pass
            |move|p1b: Red-Ghast|Metronome|p1b: Red-Ghast
            |move|p1b: Red-Ghast|Shell Smash|p1b: Red-Ghast|[from]move: Metronome
            |-unboost|p1b: Red-Ghast|def|1
            |-unboost|p1b: Red-Ghast|spd|1
            |-boost|p1b: Red-Ghast|atk|2
            |-boost|p1b: Red-Ghast|spa|2
            |-boost|p1b: Red-Ghast|spe|2
            |move|p2a: Red Muff|Metronome|p2a: Red Muff
            |move|p2a: Red Muff|Tearful Look|p1b: Red-Ghast|[from]move: Metronome
            |-unboost|p1b: Red-Ghast|atk|1
            |-unboost|p1b: Red-Ghast|spa|1
            |move|p2b: Crunchz|Metronome|p2b: Crunchz
            |move|p2b: Crunchz|Doom Desire|p1b: Red-Ghast|[from]move: Metronome
            |-start|p2b: Crunchz|Doom Desire
            |
            |upkeep
            """,
        )

        turn4 = MockTurn(
            4,
            """
            |turn|4
            |
            |t:|1698879397
            |move|p1b: Red-Ghast|Metronome|p1b: Red-Ghast
            |move|p1b: Red-Ghast|Sweet Kiss|p2a: Red Muff|[from]move: Metronome
            |-start|p2a: Red Muff|confusion
            |move|p1a: Fisterman|Metronome|p1a: Fisterman
            |move|p1a: Fisterman|Block||[from]move: Metronome|[still]
            |-fail|p1a: Fisterman
            |-activate|p2a: Red Muff|confusion
            |move|p2a: Red Muff|Metronome|p2a: Red Muff
            |move|p2a: Red Muff|Iron Defense|p2a: Red Muff|[from]move: Metronome
            |-boost|p2a: Red Muff|def|2
            |move|p2b: Crunchz|Metronome|p2b: Crunchz
            |move|p2b: Crunchz|Retaliate|p1a: Fisterman|[from]move: Metronome
            |-damage|p1a: Fisterman|74/100
            |
            |upkeep
            """,
        )

        turn5 = MockTurn(
            5,
            """
            |turn|5
            |
            |t:|1698879416
            |move|p1b: Red-Ghast|Metronome|p1b: Red-Ghast
            |move|p1b: Red-Ghast|Fairy Wind|p2b: Crunchz|[from]move: Metronome
            |-damage|p2b: Crunchz|77/100
            |move|p1a: Fisterman|Metronome|p1a: Fisterman
            |move|p1a: Fisterman|Water Spout|p2b: Crunchz|[from]move: Metronome|[spread] p2a,p2b
            |-damage|p2a: Red Muff|77/100
            |-damage|p2b: Crunchz|68/100
            |-activate|p2a: Red Muff|confusion
            |move|p2a: Red Muff|Metronome|p2a: Red Muff
            |move|p2a: Red Muff|Scratch|p1a: Fisterman|[from]move: Metronome
            |-damage|p1a: Fisterman|65/100
            |move|p2b: Crunchz|Metronome|p2b: Crunchz
            |move|p2b: Crunchz|Slack Off|p2b: Crunchz|[from]move: Metronome
            |-heal|p2b: Crunchz|100/100
            |
            |-end|p1b: Red-Ghast|move: Doom Desire
            |-damage|p1b: Red-Ghast|65/100
            |upkeep
            """,
        )

        battle.turns = [turn3, turn4, turn5]
        event = "|-damage|p1b: Red-Ghast|65/100"

        # (dealer, source)
        expected_output = ((2, "Crunchz"), "Doom Desire")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn5, battle=battle
            ),
            expected_output,
        )

    def test_ensure_return_dealer_and_source(self):
        # https://replay.pokemonshowdown.com/gen9ou-1988323885
        turn = MockTurn(
            2,
            """
            |turn|2
            |
            |t:|1699708613
            |move|p2a: Skeledirge|Dark Pulse|p1a: Zoroark
            |-supereffective|p1a: Zoroark
            |-damage|p1a: Zoroark|0 fnt
            |faint|p1a: Zoroark
            |-damage|p2a: Skeledirge|81/100|[from] item: Life Orb
            |
            |upkeep
            |
            |t:|1699708618
            |switch|p1a: Toxapex|Toxapex, M|100/100
            """,
        )
        event = "|-damage|p1a: Zoroark|0 fnt"

        # (dealer, source)
        expected_output = ((2, "Skeledirge"), "Dark Pulse")

        self.assertEqual(
            self.move_dealer_finder.get_dealer_and_source(
                event=event, turn=turn, battle=MockBattle()
            ),
            expected_output,
        )


if __name__ == "__main__":
    unittest.main()
