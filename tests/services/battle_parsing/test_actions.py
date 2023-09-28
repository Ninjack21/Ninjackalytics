# # import unittest
# # from unittest.mock import Mock
# 
# # import os
# # import sys
# 
# # file_path = os.path.dirname(os.path.realpath(__file__))
# # app_path = file_path.split("ninjackalytics")[0]
# # app_path = app_path + "ninjackalytics"
# # sys.path.insert(1, app_path)
# 
# # from app.services.battle_parsing.actions import ActionData
# 
# 
# # class TestActionData(unittest.TestCase):
# #     def setUp(self):
# #         self.mock_battle = Mock()
# #         self.mock_battle.get_log.return_value = (
# #             "|p1a|player1|rating:1500\n|p2a|player2|rating:1500\n"
# #         )
# #         self.mock_battle.get_turns.return_value = [
# #             Mock(number=1, text="|move|p1a: pikachu|tackle\n|switch|p2a: charizard"),
# #             Mock(
# #                 number=2,
# #                 text="|move|p2a: charizard|fire blast\n|move|p1a: pikachu|protect",
# #             ),
# #             Mock(number=3, text="|move|p2a: charizard|fly\n|move|p1a: pikachu|psychic"),
# #         ]
# #         self.action_data = ActionData(self.mock_battle)
# 
# #     def test_get_player_numbers(self):
# #         self.mock_battle.get_log.return_value = (
# #             "|p1a|player1|rating:1500\n|p2a|player2|rating:1500\n"
# #         )
# #         self.assertEqual(self.action_data._get_player_numbers(), [1, 2])
# 
# #     def test_get_player_action_with_move(self):
# #         turn_text = "|move|p1a: pikachu|tackle"
# #         expected_output = {"Player_Number": 1, "Action": "move"}
# #         self.assertEqual(
# #             self.action_data._get_player_action(turn_text, 1), expected_output
# #         )
# 
# #     def test_get_player_action_with_switch(self):
# #         turn_text = "|switch|p2a: charizard"
# #         expected_output = {"Player_Number": 2, "Action": "switch"}
# #         self.assertEqual(
# #             self.action_data._get_player_action(turn_text, 2), expected_output
# #         )
# 
# #     def test_get_player_action_with_no_action(self):
# #         turn_text = "|-damage|p1|25/100"
# #         expected_output = {"Player_Number": 1, "Action": "incapacitated"}
# #         self.assertEqual(
# #             self.action_data._get_player_action(turn_text, 1), expected_output
# #         )
# 
# #     def test_get_action_data(self):
# #         expected_output = [
# #             {"Player_Number": 1, "Turn": 1, "Action": "move"},
# #             {"Player_Number": 1, "Turn": 2, "Action": "move"},
# #             {"Player_Number": 1, "Turn": 3, "Action": "move"},
# #             {"Player_Number": 2, "Turn": 1, "Action": "switch"},
# #             {"Player_Number": 2, "Turn": 2, "Action": "move"},
# #             {"Player_Number": 2, "Turn": 3, "Action": "move"},
# #         ]
# #         self.assertEqual(self.action_data.get_action_data(), expected_output)
# 
# 
# # if __name__ == "__main__":
# #     unittest.main()
