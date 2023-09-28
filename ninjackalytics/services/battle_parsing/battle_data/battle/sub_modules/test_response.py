import unittest
from unittest.mock import patch, Mock
from typing import Iterable, Optional, List

from .response import Response
from .turn import Turn


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

        # Test initialization with no turns
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
