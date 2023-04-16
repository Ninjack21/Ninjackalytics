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

from app.services.battle_parsing.log_models import Response, Turn


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


if __name__ == "__main__":
    unittest.main()
