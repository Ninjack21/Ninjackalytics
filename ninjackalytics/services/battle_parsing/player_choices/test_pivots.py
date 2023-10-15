import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn, MockBattle

from . import PivotData


class TestPivotData(unittest.TestCase):
    def setUp(self):
        self.mock_battle = MockBattle()
        self.mock_battle.log = """
            |start
            |switch|p1a: May Day Parade|Kecleon, F, shiny|324/324
            |switch|p2a: AMagicalFox|Delphox, M, shiny|292/292
            |turn|1
            |callback|decision
            |
            |move|p1a: May Day Parade|Fake Out|p2a: AMagicalFox
            |-damage|p2a: AMagicalFox|213/292
            |cant|p2a: AMagicalFox|flinch
            |
            |turn|2
            |callback|decision
            |
            |-start|p1a: May Day Parade|typechange|Dark|[from] Protean
            |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox
            |-crit|p2a: AMagicalFox
            |-supereffective|p2a: AMagicalFox
            |-damage|p2a: AMagicalFox|0 fnt
            |faint|p2a: AMagicalFox
            |
            |callback|decision
            |
            |switch|p2a: Moustachio|Alakazam, M, shiny|252/252
            """

        turn1 = MockTurn(
            1,
            """1
            |callback|decision
            |
            |move|p1a: May Day Parade|Fake Out|p2a: AMagicalFox
            |-damage|p2a: AMagicalFox|213/292
            |cant|p2a: AMagicalFox|flinch
            |switch|p1a: Dragapult|Dragapult, M|28/100|[from] Teleport
            |""",
        )
        turn2 = MockTurn(
            2,
            """2
            |callback|decision
            |
            |-start|p1a: May Day Parade|typechange|Dark|[from] Protean
            |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox
            |-crit|p2a: AMagicalFox
            |-supereffective|p2a: AMagicalFox
            |-damage|p2a: AMagicalFox|0 fnt
            |faint|p2a: AMagicalFox
            |
            |callback|decision
            |
            |switch|p2a: Moustachio|Alakazam, M, shiny|252/252""",
        )

        turns = [turn1, turn2]
        self.mock_battle.turns = turns

        self.mock_battle_pokemon = MockBattlePokemon()

    def test_get_pivot_data(self):
        pivot_data = PivotData(self.mock_battle, self.mock_battle_pokemon)

        actual_response = pivot_data.get_pivot_data()

        expected_response = [
            {
                "Pokemon_Enter": "Dragapult",
                "Player_Number": 1,
                "Source_Name": "Teleport",
                "Turn": 1,
            },
            {
                "Pokemon_Enter": "Moustachio",
                "Player_Number": 2,
                "Source_Name": "action",
                "Turn": 2,
            },
        ]

        # Check no additional pivot events found
        for pivot_event in actual_response:
            self.assertIn(pivot_event, expected_response)

        # Check no missing pivot events
        for pivot_event in expected_response:
            self.assertIn(pivot_event, actual_response)


if __name__ == "__main__":
    unittest.main()
