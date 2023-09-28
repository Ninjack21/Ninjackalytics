import unittest
from unittest.mock import patch, Mock
from typing import Iterable, Optional, List


from . import Response, Turn
from .battle import Battle


class TestBattle(unittest.TestCase):
    @patch.object(Battle, "_get_json_response")
    def test__get_json_response(self, mock_get):
        # Test successful response
        json_response = {"id": "1", "format": "gen8", "log": ""}

        mock_get.return_value = json_response

        url = "http://example.com"
        battle = Battle(url)
        self.assertEqual(battle._get_json_response(), json_response)

    @patch.object(Battle, "_get_json_response")
    def test_get_turn(self, mock_get):
        # Test turn exists
        turn1 = Turn(1, "|some_event|1")
        turn2 = Turn(2, "|another_event|2")
        json_response = {
            "id": "1",
            "format": "gen8",
            "log": "|start\n|turn|" + turn1.text + "|turn|" + turn2.text,
        }
        mock_get.return_value = json_response

        battle = Battle("some_url")

        self.assertEqual(battle.get_turn(1).text, turn1.text)

        # Test turn does not exist
        self.assertIsNone(battle.get_turn(3))

    @patch.object(Battle, "_get_json_response")
    def test_get_turns(self, mock_get):
        # Test no turns
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response

        battle = Battle("some_url")

        self.assertEqual(list(battle.get_turns()), [])

        # Test multiple turns
        turn0 = Turn(0, "")
        turn1 = Turn(1, "|some_event|1")
        turn2 = Turn(2, "|another_event|2")
        json_response = {
            "id": "1",
            "format": "gen8",
            "log": "|start\n"
            + turn0.text
            + "|turn|"
            + turn1.text
            + "|turn|"
            + turn2.text,
        }
        mock_get.return_value = json_response

        battle = Battle("some_url")

        self.assertEqual(
            [turn.text for turn in battle.get_turns()],
            [turn0.text, turn1.text, turn2.text],
        )

    @patch.object(Battle, "_get_json_response")
    def test_get_id(self, mock_get):
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response
        battle = Battle("some_url")

        self.assertEqual(battle.get_id(), "1")

    @patch.object(Battle, "_get_json_response")
    def test_get_format(self, mock_get):
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response

        battle = Battle("some_url")

        self.assertEqual(battle.get_format(), "gen8")

    @patch.object(Battle, "_get_json_response")
    def test_get_log(self, mock_get):
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response

        battle = Battle("some_url")

        self.assertEqual(battle.get_log(), "")

    @patch.object(Battle, "_get_json_response")
    def test_get_lines(self, mock_get):
        log = """
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
        json_response = {"id": "1", "format": "gen8", "log": log}
        mock_get.return_value = json_response

        battle = Battle("some_url")

        lines = battle.get_lines()
        log_lines = [
            line
            for line in log.split("\n")
            if bool(line.strip()) and "|start" not in line
        ]

        # Test that all lines appear and in the presumed order
        for i, line in enumerate(lines):
            # simple log_lines for test don't remove |turn| from lines that indicate new turns
            # only test loglines where |turn| not in it since not worried about this behavior
            if "|turn|" not in log_lines[i]:
                self.assertEqual(line.text, log_lines[i])


if __name__ == "__main__":
    unittest.main()
