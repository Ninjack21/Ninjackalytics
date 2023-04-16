import unittest
from unittest.mock import patch, Mock
from typing import Iterable, Optional, List
import requests_mock


import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.log_models import Turn, Line


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


if __name__ == "__main__":
    unittest.main()
