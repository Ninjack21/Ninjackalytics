# # import unittest
# # from unittest.mock import MagicMock, Mock
# 
# # import os
# # import sys
# 
# # file_path = os.path.dirname(os.path.realpath(__file__))
# # app_path = file_path.split("ninjackalytics")[0]
# # app_path = app_path + "ninjackalytics"
# # sys.path.insert(1, app_path)
# 
# # from app.services.battle_parsing import BattleParser, Battle, BattlePokemon
# 
# 
# # class TestBattleParser(unittest.TestCase):
# #     def setUp(self):
# #         self.mock_url = "mock_url"
# #         self.mock_battle = MagicMock(spec=Battle)
# #         self.mock_battle_pokemon = MagicMock(spec=BattlePokemon)
# #         self.mock_battle_pokemon.teams = ["Team1", "Team2"]
# #         self.battle_parser = BattleParser(self.mock_battle, self.mock_battle_pokemon)
# 
# #     def test_analyze_battle(self):
# #         # Mock the behavior of the different parsing modules
# #         self.battle_parser.battle_data.get_db_info = MagicMock(
# #             return_value="mock_general_info"
# #         )
# #         self.battle_parser.pivot_data.get_pivot_data = MagicMock(
# #             return_value="mock_pivot_info"
# #         )
# #         self.battle_parser.action_data.get_action_data = MagicMock(
# #             return_value="mock_action_info"
# #         )
# #         self.battle_parser.hp_events_handler.handle_events = Mock()
# #         self.battle_parser.hp_events_handler.get_damage_events = MagicMock(
# #             return_value="mock_damages_info"
# #         )
# #         self.battle_parser.hp_events_handler.get_heal_events = MagicMock(
# #             return_value="mock_heals_info"
# #         )
# 
# #         # Call the analyze_battle method
# #         self.battle_parser.analyze_battle()
# 
# #         # Check if the attributes have been updated correctly
# #         self.assertEqual(self.battle_parser.general_info, "mock_general_info")
# #         self.assertEqual(self.battle_parser.pivot_info, "mock_pivot_info")
# #         self.assertEqual(self.battle_parser.action_info, "mock_action_info")
# #         self.assertEqual(self.battle_parser.damages_info, "mock_damages_info")
# #         self.assertEqual(self.battle_parser.heals_info, "mock_heals_info")
# #         self.assertEqual(self.battle_parser.teams, ["Team1", "Team2"])
# 
# #         # Check that handle_events was called
# #         self.battle_parser.hp_events_handler.handle_events.assert_called_once()
# 
# 
# # if __name__ == "__main__":
# #     unittest.main()
