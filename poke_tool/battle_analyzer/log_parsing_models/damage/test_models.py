import unittest
from unittest.mock import Mock

from models import (
    Turn,
    Battle,
    BattlePokemon,
    DamageData,
    ItemOrAbilityDataFinder,
    StatusOrHazardDataFinder,
    PassiveDataFinder,
    DamageData,
    MoveDealerFinder,
)

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


class TestMoveDealerFinder(unittest.TestCase):
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
        |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroarp1b: Dragapult|Dragon Darts|p2b: Incineroar
        |-damage|p2b: Incineroar|31/100
        """
        self.normalturn = MockTurn(
            1,
            """
            |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
            |-damage|p1a: Cuss-Tran|67/100
            """,
        )
        self.delayedturn = MockTurn(
            17,
            """
            |-end|p1a: Ninetales|move: Future Sight
            |-damage|p1a: Ninetales|44/100
            """,
        )
        self.doublesturn1 = MockTurn(
            3, "|move|p2a: Genesect|Techno Blast|p1a: Palossand"
        )
        self.doublesturn2 = MockTurn(
            4, "|move|p1a: Palossand|Scorching Sands|p2b: Incineroar"
        )
        self.animatedturn = MockTurn(
            5,
            """
            |move|p1b: Dragapult|Dragon Darts|p2b: Incineroar
            |-damage|p2b: Incineroar|76/100
            |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
            |-damage|p2b: Incineroar|52/100
            """,
        )

        self.move_dealer_finder = MoveDealerFinder(mock_battle_pokemon)

    def test_get_normal_dealer_and_source(self):
        # test expected case
        # (dealer, source)
        expected_output = ((2, "Blissey"), "Seismic Toss")
        self.assertEqual(
            self.move_dealer_finder._get_normal_dealer_and_source(
                event="|-damage|p1a: Cuss-Tran|67/100",
                receiver_raw="p1a: Cuss-Tran",
                turn=self.normalturn,
            ),
            expected_output,
        )

        # test bad input case
        bad_turn_text = "a bad turn text"
        with self.assertRaises(ValueError):
            self.move_dealer_finder._get_normal_dealer_and_source(
                event="|-damage|p1a: Cuss-Tran|67/100",
                receiver_raw="p1a: Cuss-Tran",
                turn=MockTurn(1, bad_turn_text),
            )

    def test_get_delayed_dealer_and_source(self):
        mock_battle = MockBattle()
        fsight_start_turn = MockTurn(
            14,
            """
            |move|p2a: Slowking|Future Sight|p1a: Ninetales
            |-start|p2a: Slowking|move: Future Sight
            """,
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
                receiver_raw="p1a: Ninetales",
                turn=self.delayedturn,
                battle=mock_battle,
            ),
            expected_output,
        )


# class TestDamageData(unittest.TestCase):
#     def setUp(self):
#         """
#         normal:
#         -------
#         |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
#         |-damage|p1a: Cuss-Tran|67/100

#         delayed:
#         --------
#         |turn|14
#         ...
#         |move|p2a: Slowking|Future Sight|p1a: Ninetales
#         |-start|p2a: Slowking|move: Future Sight
#         ...
#         |turn|15
#         ...
#         |turn|16
#         ...
#         |-end|p1a: Ninetales|move: Future Sight
#         |-damage|p1a: Ninetales|44/100
#         ...
#         |turn|17

#         doubles:
#         --------
#         |move|p2a: Genesect|Techno Blast|p1a: Palossand
#         |-damage|p1a: Palossand|65/100
#         |move|p1a: Palossand|Scorching Sands|p2b: Incineroar
#         |-damage|p2b: Incineroar|76/100

#         doubles_anim:
#         -------------
#         |-anim||move|p1b: Dragapult|Dragon Darts|p2a: Pelipper
#         |-damage|p2a: Pelipper|65/100
#         |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroarp1b: Dragapult|Dragon Darts|p2b: Incineroar
#         |-damage|p2b: Incineroar|31/100
#         """

#         self.normalturn = MockTurn(
#             1,
#             """
#             |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
#             |-damage|p1a: Cuss-Tran|67/100
#             """,
#         )
#         self.delayedturn = MockTurn(
#             17,
#             """
#             |-end|p1a: Ninetales|move: Future Sight
#             |-damage|p1a: Ninetales|44/100
#             """,
#         )
#         self.doublesturn1 = MockTurn(3, "|move|p2a: Genesect|Techno Blast|p1a: Palossand")
#         self.doublesturn2 = MockTurn(
#             4, "|move|p1a: Palossand|Scorching Sands|p2b: Incineroar"
#         )
#         self.animatedturn = MockTurn(
#             5,
#             """
#             |move|p1b: Dragapult|Dragon Darts|p2b: Incineroar
#             |-damage|p2b: Incineroar|76/100
#             |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
#             |-damage|p2b: Incineroar|52/100
#             """,
#         )

#     def test_normal_get_damage_data(self):
#         # not needed for normal
#         mock_battle = Mock()

#         expected_output = {
#             "Dealer": "Blissey",
#             "Dealer_Player_Number": 2,
#             "Receiver": "Cuss-Tran",
#             "Receiver_Player_Number": 1,
#             "Source_Name": "Seismic Toss",
#             "Damage": 33.0,
#             "Type": "Move",
#             "Turn": 1,
#         }
#         actual_output = DamageData.get_damage_data(
#             "|-damage|p1a: Cuss-Tran|67/100", self.normalturn, mock_battle
#         )
#         self.assertEqual(actual_output, expected_output)

#     def test_delayed_get_damage_data(self):
#         mock_battle = MockBattle()
#         fsight_start_turn = MockTurn(
#             14,
#             """
#             |move|p2a: Slowking|Future Sight|p1a: Ninetales
#             |-start|p2a: Slowking|move: Future Sight
#             """,
#         )
#         fsight_middle_turn = MockTurn(
#             15,
#             """
#             |
#             |t:|1680411602
#             |switch|p2a: Clefable|Clefable, M|100/100
#             |move|p1a: Ninetales|Aurora Veil|p1a: Ninetales
#             |-sidestart|p1: rhkp23|move: Aurora Veil
#             |
#             |-weather|Hail|[upkeep]
#             |upkeep
#             """,
#         )
#         fsight_end_turn = self.delayedturn
#         mock_battle.turns = [fsight_start_turn, fsight_middle_turn, fsight_end_turn]

#         expected_output = {
#             "Dealer": "Slowking",
#             "Dealer_Player_Number": 2,
#             "Receiver": "Ninetales",
#             "Receiver_Player_Number": 1,
#             "Source_Name": "Future Sight",
#             "Damage": 56.0,
#             "Type": "Move",
#             "Turn": 17,
#         }
#         actual_output = DamageData.get_damage_data(
#             "|-damage|p1a: Ninetales|44/100", self.delayedturn, mock_battle
#         )

#         self.assertEqual(actual_output, expected_output)

#     def test_doubles_get_damage_data(self):
#         mock_battle = MockBattle()

#         expected_output = {
#             "Dealer": "Genesect",
#             "Dealer_Player_Number": 2,
#             "Receiver": "Palossand",
#             "Receiver_Player_Number": 1,
#             "Source_Name": "Techno Blast",
#             "Damage": 35.0,
#             "Type": "Move",
#             "Turn": 3,
#         }
#         actual_output = DamageData.get_damage_data(
#             "|-damage|p1a: Palossand|65/100", self.doublesturn1, mock_battle
#         )

#         self.assertEqual(actual_output, expected_output)

#     def test_animated_get_damage_data(self):
#         mock_battle = MockBattle()

#         expected_output = {
#             "Dealer": "Dragapult",
#             "Dealer_Player_Number": 1,
#             "Receiver": "Incineroar",
#             "Receiver_Player_Number": 2,
#             "Source_Name": "Dragon Darts",
#             "Damage": 69.0,
#             "Type": "Move",
#             "Turn": 5,
#         }
#         actual_output = DamageData.get_damage_data(
#             "|-damage|p2b: Incineroar|31/100", self.animatedturn, mock_battle
#         )

#         self.assertEqual(actual_output, expected_output)


class TestItemOrAbilityDataFinder(unittest.TestCase):
    def setUp(self):

        self.item_or_ability_data_finder = ItemOrAbilityDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test case 1
        event1 = "|-damage|p2a: BrainCell|372/424|[from] item: Life Orb"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Life Orb",
            "Dealer_Player_Number": 2,
            "Receiver": "BrainCell",
            "Receiver_Player_Number": 2,
            "Source_Name": "Life Orb",
            "Damage": (52 / 424) * 100,
            "Type": "Item",
            "Turn": 1,
        }
        actual_output1 = self.item_or_ability_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test case 2
        event2 = "|-damage|p1a: Pikachu|120/169|[from] ability: Static"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "Static",
            "Dealer_Player_Number": 1,
            "Receiver": "Pikachu",
            "Receiver_Player_Number": 1,
            "Source_Name": "Static",
            "Damage": (49 / 169) * 100,
            "Type": "Ability",
            "Turn": 5,
        }
        actual_output2 = self.item_or_ability_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 3 - event without item or ability damage
        with self.assertRaises(ValueError):
            event3 = "|-damage|p1a: Pikachu|120/169"
            turn3 = MockTurn(5, event3)
            self.item_or_ability_data_finder.get_damage_data(event3, turn3)


class TestStatusorHazardDataFinder(unittest.TestCase):
    def setUp(self):

        self.status_hazard_data_finder = StatusOrHazardDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test hazard damage
        event1 = "|-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Stealth Rock",
            "Dealer_Player_Number": 1,
            "Receiver": "Ferrothorn",
            "Receiver_Player_Number": 2,
            "Source_Name": "Stealth Rock",
            "Damage": (6 / 100) * 100,
            "Type": "Hazard",
            "Turn": 1,
        }
        actual_output1 = self.status_hazard_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test toxic damage
        event2 = "|-damage|p1a: Rillaboom|94/100 tox|[from] psn"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "tox",
            "Dealer_Player_Number": 2,
            "Receiver": "Rillaboom",
            "Receiver_Player_Number": 1,
            "Source_Name": "tox",
            "Damage": (6 / 100) * 100,
            "Type": "Status",
            "Turn": 5,
        }
        actual_output2 = self.status_hazard_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test normal poison damage
        event2 = "|-damage|p1a: Jigglypuff|94/100|[from] psn"
        turn2 = MockTurn(5, event2)

        expected_output2 = {
            "Dealer": "psn",
            "Dealer_Player_Number": 2,
            "Receiver": "Jigglypuff",
            "Receiver_Player_Number": 1,
            "Source_Name": "psn",
            "Damage": (6 / 100) * 100,
            "Type": "Status",
            "Turn": 5,
        }
        actual_output2 = self.status_hazard_data_finder.get_damage_data(event2, turn2)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 4 - event without status or hazard
        with self.assertRaises(ValueError):
            event3 = "|-damage|p1a: Pikachu|120/169"
            turn3 = MockTurn(5, event3)
            self.status_hazard_data_finder.get_damage_data(event3, turn3)


class TestPassiveDataFinder(unittest.TestCase):
    def setUp(self):

        self.passive_data_finder = PassiveDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test passive damage with obvious dealer
        event1 = "|-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn"
        turn1 = MockTurn(1, event1)

        expected_output1 = {
            "Dealer": "Ferrothorn",
            "Dealer_Player_Number": 2,
            "Receiver": "Druddigon",
            "Receiver_Player_Number": 1,
            "Source_Name": "Leech Seed",
            "Damage": (12 / 100) * 100,
            "Type": "Passive",
            "Turn": 1,
        }
        actual_output1 = self.passive_data_finder.get_damage_data(event1, turn1)
        # round to 2 decimal places
        expected_output1["Damage"] = round(expected_output1["Damage"], 2)
        actual_output1["Damage"] = round(actual_output1["Damage"], 2)

        self.assertEqual(
            actual_output1,
            expected_output1,
        )

        # Test passive damage without [of]
        # NOTE: as seen in code, I do not currently know of case where this exists
        event2 = "|-damage|p1a: Aggron|88/100|[from] something weird"
        turn1 = MockTurn(1, event2)

        expected_output2 = {
            "Dealer": "something weird",
            "Dealer_Player_Number": 2,
            "Receiver": "Aggron",
            "Receiver_Player_Number": 1,
            "Source_Name": "something weird",
            "Damage": (12 / 100) * 100,
            "Type": "Passive",
            "Turn": 1,
        }
        actual_output2 = self.passive_data_finder.get_damage_data(event2, turn1)
        # round to 2 decimal places
        expected_output2["Damage"] = round(expected_output2["Damage"], 2)
        actual_output2["Damage"] = round(actual_output2["Damage"], 2)

        self.assertEqual(
            actual_output2,
            expected_output2,
        )

        # Test case 3 - weather damage
        event3 = "|-damage|p1a: Seismitoad|6/100|[from] Hail"
        turn3 = MockTurn(5, event3)

        expected_output3 = {
            "Dealer": "Hail",
            "Dealer_Player_Number": 2,
            "Receiver": "Seismitoad",
            "Receiver_Player_Number": 1,
            "Source_Name": "Hail",
            "Damage": (94 / 100) * 100,
            "Type": "Passive",
            "Turn": 5,
        }
        actual_output3 = self.passive_data_finder.get_damage_data(event3, turn3)
        # round to 2 decimal places
        expected_output3["Damage"] = round(expected_output3["Damage"], 2)
        actual_output3["Damage"] = round(actual_output3["Damage"], 2)

        self.assertEqual(
            actual_output3,
            expected_output3,
        )

        # Test case 4 - no [from] found (would normally indidcate a move damage)
        with self.assertRaises(ValueError):
            event3 = "|-damage|p2a: Ferrothorn|94/100|"
            turn3 = MockTurn(5, event3)
            self.passive_data_finder.get_damage_data(event3, turn3)


# TODO: turn back on once all other objects are tested and passing
# class TestDamageData(unittest.TestCase):
#     def setUp(self):
#         self.mock_battle = Mock(spec=Battle)
#         self.mock_battle_pokemon = Mock(spec=BattlePokemon)
#         self.damage_data = DamageData(self.mock_battle, self.mock_battle_pokemon)

#     def test_get_source(self):
#         test_cases = [
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292",
#                 "expected_source": "move",
#             },
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292|[from] item: Life Orb",
#                 "expected_source": "item",
#             },
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292|[from] ability: Rough Skin",
#                 "expected_source": "ability",
#             },
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292|[from] Stealth Rock",
#                 "expected_source": "hazard",
#             },
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292|[from] psn",
#                 "expected_source": "status",
#             },
#             {
#                 "event": "|-damage|p2a: AMagicalFox|213/292|[from] some_unknown_event",
#                 "expected_source": "passive",
#             },
#         ]

#         for test_case in test_cases:
#             event = test_case["event"]
#             expected_source = test_case["expected_source"]
#             actual_source = self.damage_data.get_source(event)

#             self.assertEqual(
#                 actual_source, expected_source, f"Failed for event: {event}"
#             )


if __name__ == "__main__":
    unittest.main()
