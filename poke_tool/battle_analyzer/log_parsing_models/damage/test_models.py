import unittest
from unittest.mock import Mock

from models import DamageData, SingleBattle, MultiBattle, Turn, Battle, BattlePokemon


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
