import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn, MockBattle

from . import ActionData


class TestActionData(unittest.TestCase):
    def setUp(self):
        self.mock_battle = MockBattle()
        self.mock_battle.log = "|p1a|player1|rating:1500\n|p2a|player2|rating:1500\n"

        turn1 = MockTurn(1, "|move|p1a: pikachu|tackle\n|switch|p2a: charizard")
        turn2 = MockTurn(
            2, "|move|p2a: charizard|fire blast\n|move|p1a: pikachu|protect"
        )
        turn3 = MockTurn(3, "|move|p2a: charizard|fly\n|move|p1a: pikachu|psychic")
        turns = [turn1, turn2, turn3]

        self.mock_battle.turns = turns
        self.action_data = ActionData(self.mock_battle)

    def test_get_player_numbers(self):
        self.assertEqual(self.action_data._get_player_numbers(), [1, 2])

    def test_get_player_action_with_move(self):
        turn_text = "|move|p1a: pikachu|tackle"
        expected_output = {"Player_Number": 1, "Action": "move"}
        self.assertEqual(
            self.action_data._get_player_action(turn_text, 1), expected_output
        )

    def test_get_player_action_with_switch(self):
        turn_text = "|switch|p2a: charizard"
        expected_output = {"Player_Number": 2, "Action": "switch"}
        self.assertEqual(
            self.action_data._get_player_action(turn_text, 2), expected_output
        )

    def test_get_player_action_with_no_action(self):
        turn_text = "|-damage|p1|25/100"
        expected_output = {"Player_Number": 1, "Action": "incapacitated"}
        self.assertEqual(
            self.action_data._get_player_action(turn_text, 1), expected_output
        )

    def test_get_action_data(self):
        expected_output = [
            {"Player_Number": 1, "Turn": 1, "Action": "move"},
            {"Player_Number": 1, "Turn": 2, "Action": "move"},
            {"Player_Number": 1, "Turn": 3, "Action": "move"},
            {"Player_Number": 2, "Turn": 1, "Action": "switch"},
            {"Player_Number": 2, "Turn": 2, "Action": "move"},
            {"Player_Number": 2, "Turn": 3, "Action": "move"},
        ]
        self.assertEqual(self.action_data.get_action_data(), expected_output)


if __name__ == "__main__":
    unittest.main()
