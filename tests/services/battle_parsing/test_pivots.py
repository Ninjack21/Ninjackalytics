import unittest
from unittest.mock import Mock


import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.pivots import PivotData


class TestPivotData(unittest.TestCase):
    def setUp(self):
        self.mock_battle = Mock()
        self.mock_battle.get_log.return_value = """
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
        self.mock_battle.get_turns.return_value = [
            Mock(
                number=1,
                text="""1
            |callback|decision
            |
            |move|p1a: May Day Parade|Fake Out|p2a: AMagicalFox
            |-damage|p2a: AMagicalFox|213/292
            |cant|p2a: AMagicalFox|flinch
            |switch|p1a: Dragapult|Dragapult, M|28/100|[from] Teleport
            |""",
            ),
            Mock(
                number=2,
                text="""2
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
            ),
        ]

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
