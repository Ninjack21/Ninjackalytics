# # import unittest
# # from unittest.mock import MagicMock
# # from datetime import datetime
# 
# 
# # import os
# # import sys
# 
# # file_path = os.path.dirname(os.path.realpath(__file__))
# # app_path = file_path.split("ninjackalytics")[0]
# # app_path = app_path + "ninjackalytics"
# # sys.path.insert(1, app_path)
# 
# # from app.services.battle_parsing.battle_data import BattleData
# 
# 
# # class TestBattleData(unittest.TestCase):
# #     def setUp(self):
# #         """
# #         I need to go find real examples of the different parts of the logs that we care about to
# #         update these with so that our tests will be used against examples that are realistic.
# #         """
# #         self.battle_mock = MagicMock()
# #         self.battle_mock.get_log.return_value = """
# #         |player|p1|kdarewolf|37
# #         |player|p2|Onox|159
# #         |rated
# #         |...
# #         |win|kdarewolf
# #         |raw|Ladder updating...
# #         |leave|Onox
# #         |player|p2
# #         |raw|kdarewolf's rating: 1049 &rarr; <strong>1076</strong><br />(+27 for winning)
# #         |raw|Onox's rating: 1087 &rarr; <strong>1059</strong><br />(-28 for losing)
# #         """
# #         self.battle_mock.get_id.return_value = "12345"
# #         self.battle_mock.get_format.return_value = "gen6oumonotype"
# #         self.battle_pokemon_mock = MagicMock()
# #         self.battle_pokemon_mock.teams = [
# #             "Charizard",
# #             "Pikachu",
# #             "Bulbasaur",
# #             "Squirtle",
# #         ]
# #         self.battle_data = BattleData(self.battle_mock, self.battle_pokemon_mock)
# 
# #     def test_get_db_info(self):
# #         db_info = self.battle_data.get_db_info()
# #         self.assertIsInstance(db_info, dict)
# #         self.assertIn("Battle_ID", db_info)
# #         self.assertEqual(db_info["Battle_ID"], "12345")
# #         self.assertIn("Format", db_info)
# #         self.assertEqual(db_info["Format"], "gen6oumonotype")
# #         self.assertIn("P1", db_info)
# #         self.assertIn("P2", db_info)
# #         self.assertIn("Rank", db_info)
# #         self.assertIn("Winner", db_info)
# #         self.assertIn("Date_Submitted", db_info)
# #         self.assertIsInstance(db_info["Date_Submitted"], datetime)
# 
# #     def test_return_general_info(self):
# #         general_info = self.battle_data._return_general_info()
# #         self.assertIsInstance(general_info, dict)
# #         self.assertIn("Battle_ID", general_info)
# #         self.assertEqual(general_info["Battle_ID"], "12345")
# #         self.assertIn("Format", general_info)
# #         self.assertEqual(general_info["Format"], "gen6oumonotype")
# #         self.assertIn("Date_Submitted", general_info)
# #         self.assertIsInstance(general_info["Date_Submitted"], datetime)
# 
# #     def test_parse_player_names(self):
# #         player_names = self.battle_data._parse_player_names()
# #         self.assertIsInstance(player_names, dict)
# #         self.assertIn("P1", player_names)
# #         self.assertEqual(player_names["P1"], "kdarewolf")
# 
# #         self.assertIn("P2", player_names)
# #         self.assertEqual(player_names["P2"], "Onox")
# 
# #     def test_parse_rank(self):
# #         rank = self.battle_data._parse_rank()
# #         self.assertIsInstance(rank, dict)
# #         self.assertIn("Rank", rank)
# #         self.assertEqual(rank["Rank"], 1049)
# 
# #     def test_parse_winner(self):
# #         winner = self.battle_data._parse_winner()
# #         self.assertIsInstance(winner, dict)
# #         self.assertIn("Winner", winner)
# #         self.assertEqual(winner["Winner"], "kdarewolf")
# 
# #     def test_findall_regex(self):
# #         pattern = r"[0-9]+ \&rarr"
# #         matches = self.battle_data._findall_regex(pattern)
# #         self.assertIsInstance(matches, list)
# #         self.assertEqual(len(matches), 2)
# #         self.assertEqual(matches[0], "1049 &rarr")
# 
# 
# # if __name__ == "__main__":
# #     unittest.main()
