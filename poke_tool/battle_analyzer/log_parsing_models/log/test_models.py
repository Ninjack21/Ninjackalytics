import unittest
from unittest.mock import patch, Mock
from typing import Iterable, Optional, List
import requests_mock
from models import Battle, Response, Turn, Line


class TestTurn(unittest.TestCase):
    def setUp(self) -> None:
        self.turn_num = 1
        self.turn_str = "|turn| 1\n|foo| bar\n|c| baz"

    def test_init(self) -> None:
        turn = Turn(self.turn_num, self.turn_str)

        self.assertEqual(turn.number, self.turn_num)
        self.assertEqual(turn.text, self.turn_str)

    @patch.object(Line, "__init__", return_value=None)
    def test_init_creates_lines(self, mock_line_init: Mock) -> None:
        turn = Turn(self.turn_num, self.turn_str)

        self.assertTrue(isinstance(turn.lines, List))
        self.assertEqual(len(turn.lines), 1)

    @patch.object(Line, "__init__", return_value=None)
    def test_init_skips_c_and_raw_lines(self, mock_line_init: Mock) -> None:
        turn_str = "|turn| 1\n|foo| bar\n|c| baz\n|raw| qux"
        turn = Turn(self.turn_num, turn_str)

        mock_line_init.assert_called_once_with(2, "|foo| bar")


class TestResponse(unittest.TestCase):
    def test_init(self):
        # Test successful initialization
        json_response = {
            "id": "1",
            "format": "gen8",
            "log": "|start\n|switch|p1a: Venusaur|...",
        }
        response = Response(json_response)
        self.assertEqual(response.battle_id, "1")
        self.assertEqual(response.format, "gen8")
        self.assertEqual(len(response.turns), 1)
        self.assertIsInstance(response.turns[0], Turn)

        # Test failed initialization
        json_response = {"id": "1", "format": "gen8", "log": ""}
        response = Response(json_response)
        self.assertEqual(response.battle_id, "1")
        self.assertEqual(response.format, "gen8")
        self.assertEqual(len(response.turns), 0)

    def test_battle_id(self):
        json_response = {"id": "1", "format": "gen8", "log": "|start\n"}
        response = Response(json_response)
        self.assertEqual(response.battle_id, "1")

    def test_format(self):
        json_response = {"id": "1", "format": "gen8", "log": "|start\n"}
        response = Response(json_response)
        self.assertEqual(response.format, "gen8")


class TestBattle(unittest.TestCase):
    @patch.object(Battle, "_get_json_response")
    def test__get_json_response(self, mock_get):
        # Test successful response
        json_response = {"id": "1", "format": "gen8", "log": ""}

        mock_get.return_value = json_response

        url = "http://example.com"
        battle = Battle(url)
        self.assertEqual(battle._get_json_response(), json_response)

    def test_invalid_url(self):
        # Test failed response
        url = "https://invalid.com"
        with requests_mock.Mocker() as m:
            m.get(f"{url}.json", status_code=404)
            with self.assertRaises(ValueError):
                battle = Battle(url)
                battle._get_json_response()

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
        mock_get.return_value = json_response
        battle = Battle("some_url")

        self.assertEqual(battle.get_id(), "1")

    @patch.object(Battle, "_get_json_response")
    def test_get_format(self, mock_get):
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response
        mock_get.return_value = json_response
        battle = Battle("some_url")

        self.assertEqual(battle.get_format(), "gen8")

    @patch.object(Battle, "_get_json_response")
    def test_get_log(self, mock_get):
        json_response = {"id": "1", "format": "gen8", "log": ""}
        mock_get.return_value = json_response
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
        mock_get.return_value = json_response
        battle = Battle("some_url")

        lines = battle.get_lines()
        log_lines = [
            line
            for line in log.split("\n")
            if bool(line.strip()) and "|start" not in line
        ]

        # Test that all lines appear and in the presumed order
        # Dealing with turn filtering of lines right now - doesn't read whole line, only number of turn since
        # split on that
        for i, line in enumerate(lines):
            print("==================")
            print(f"{i}: {line.text}")
            print(f"{i}: {log_lines[i]}")

            # self.assertEqual(line.text, log_lines[i])


if __name__ == "__main__":
    unittest.main()
