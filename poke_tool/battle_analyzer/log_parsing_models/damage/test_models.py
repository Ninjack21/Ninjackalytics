import unittest
from unittest.mock import Mock

from models import (
    Turn,
    Battle,
    BattlePokemon,
    DamageData,
    ItemOrAbilityDataFinder,
)

# =================== MOCK PROTOCOLS FOR TESTING ===================
# based on protocol in models
class MockBattlePokemon:
    def __init__(self):
        pass

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

    # TODO: finish mocking battle pokemon methods and other protocl mocks needed


# =================== MOCK PROTOCOLS FOR TESTING ===================


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


class TestItemOrAbilityDataFinder(unittest.TestCase):
    def setUp(self):

        self.item_or_ability_data_finder = ItemOrAbilityDataFinder(mock_battle_pokemon)

    def test_get_damage_data(self):
        # Test case 1
        event1 = "|-damage|p2a: BrainCell|372/424|[from] item: Life Orb"
        turn1 = Mock()
        turn1.number = 1

        expected_output1 = {
            "Dealer": "Life Orb",
            "Dealer_Player_Number": 2,
            "Receiver": "BrainCell",
            "Receiver_Player_Number": 2,
            "Source_Name": "Life Orb",
            "Damage": 52,
            "Type": "item",
            "Turn": 1,
        }

        self.assertEqual(
            self.item_or_ability_data_finder.get_damage_data(event1, turn1),
            expected_output1,
        )

        # Test case 2
        event2 = "|-damage|p1a: Pikachu|120/169|[from] ability: Static"
        turn5 = Mock()
        turn5.number = 5

        expected_output2 = {
            "Dealer": "Static",
            "Dealer_Player_Number": 1,
            "Receiver": "Pikachu",
            "Receiver_Player_Number": 1,
            "Source_Name": "Static",
            "Damage": 49,
            "Type": "ability",
            "Turn": 5,
        }

        self.assertEqual(
            self.item_or_ability_data_finder.get_damage_data(event2, turn2),
            expected_output2,
        )

        # Test case 3 - event without item or ability damage
        event3 = "|-damage|p1a: Pikachu|120/169"
        turn3 = Mock()
        turn3.number = 3

        self.assertIsNone(
            self.item_or_ability_data_finder.get_damage_data(event3, turn3)
        )


if __name__ == "__main__":
    unittest.main()
