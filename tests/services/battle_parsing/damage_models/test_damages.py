# import unittest
# from unittest.mock import Mock
# 
# import os
# import sys
# 
# file_path = os.path.dirname(os.path.realpath(__file__))
# app_path = file_path.split("ninjackalytics")[0]
# app_path = app_path + "ninjackalytics"
# sys.path.insert(1, app_path)
# 
# from app.services.battle_parsing.damage_models.damages import DamageData
# 
# 
# # =================== MOCK PROTOCOLS FOR TESTING ===================
# # based on protocol in models
# class MockBattlePokemon:
#     def __init__(self):
#         self.mon_hps = {}
#         self.mon_hp_changes = {}
# 
#     # quick implementation for testing
#     def get_pnum_and_name(self, raw_name):
#         """
#         example raw_name = 'p1a: May Day Parade'
#         """
#         pnum_split_name = raw_name.split(": ")
#         pnum = int(pnum_split_name[0][1])
#         name = pnum_split_name[1]
#         return pnum, name
# 
#         self.mock_battle_pokemon = MockBattlePokemon()
# 
#     def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
#         if not raw_name in self.mon_hps:
#             self.mon_hps[raw_name] = 100.0
# 
#         current_hp = self.mon_hps[raw_name]
#         self.mon_hp_changes[raw_name] = new_hp - current_hp
#         self.mon_hps[raw_name] = new_hp
# 
#     def get_pokemon_hp_change(self, raw_name: str) -> float:
#         # assumes not called before get_current_hp, which inits mon_hps
#         return self.mon_hp_changes[raw_name]
# 
#     def get_pokemon_current_hp(self, raw_name: str) -> float:
#         if not raw_name in self.mon_hps:
#             self.mon_hps[raw_name] = 100.0
#         return self.mon_hps[raw_name]
# 
# 
# mock_battle_pokemon = MockBattlePokemon()
# 
# 
# class MockBattle:
#     def __init__(self):
#         turns = []
# 
#     # quick implementation for testing
#     def get_turns(self) -> list:
#         return self.turns
# 
# 
# mock_battle = MockBattle()
# 
# 
# class MockTurn:
#     def __init__(self, number: int, text: str):
#         self.number = number
#         self.text = text
# 
# 
# # =================== MOCK PROTOCOLS FOR TESTING ===================
# 
# 
# # =================== useful functions for testing ===================
# def strip_leading_spaces(text: str) -> str:
#     return "\n".join(line.lstrip() for line in text.strip().split("\n"))
# 
# 
# class TestDamageData(unittest.TestCase):
#     def setUp(self):
#         self.damage_data = DamageData(mock_battle, mock_battle_pokemon)
# 
#     def tearDown(self):
#         self.damage_data.damage_events = []
# 
#     def test_get_dmg_data(self):
#         move_turn = MockTurn(
#             1,
#             strip_leading_spaces(
#                 """
#                 |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
#                 |-damage|p1a: Cuss-Tran|67/100
#                 """
#             ),
#         )
# 
#         event = "|-damage|p1a: Cuss-Tran|67/100"
# 
#         self.damage_data.get_damage_data(event, move_turn)
#         dmg_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(dmg_data["Damage"], 33)
#         self.assertEqual(dmg_data["Dealer"], "Blissey")
#         self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
#         self.assertEqual(dmg_data["Source_Name"], "Seismic Toss")
#         self.assertEqual(dmg_data["Receiver"], "Cuss-Tran")
#         self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
#         self.assertEqual(dmg_data["Turn"], 1)
#         self.assertEqual(dmg_data["Type"], "Move")
# 
#     def test_get_item_data(self):
#         event = "|-damage|p2a: BrainCell|50/100|[from] item: Life Orb"
#         turn = MockTurn(1, event)
# 
#         self.damage_data.get_damage_data(event, turn)
#         item_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(item_data["Damage"], 50)
#         self.assertEqual(item_data["Dealer"], "Life Orb")
#         self.assertEqual(item_data["Dealer_Player_Number"], 2)
#         self.assertEqual(item_data["Source_Name"], "Life Orb")
#         self.assertEqual(item_data["Receiver"], "BrainCell")
#         self.assertEqual(item_data["Receiver_Player_Number"], 2)
#         self.assertEqual(item_data["Turn"], 1)
#         self.assertEqual(item_data["Type"], "Item")
# 
#     def test_get_ability_data(self):
#         event = "|-damage|p1a: Pikachu|80/100|[from] ability: Static"
#         turn = MockTurn(1, event)
# 
#         self.damage_data.get_damage_data(event, turn)
#         ability_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(ability_data["Damage"], 20)
#         self.assertEqual(ability_data["Dealer"], "Static")
#         self.assertEqual(ability_data["Dealer_Player_Number"], 1)
#         self.assertEqual(ability_data["Source_Name"], "Static")
#         self.assertEqual(ability_data["Receiver"], "Pikachu")
#         self.assertEqual(ability_data["Receiver_Player_Number"], 1)
#         self.assertEqual(ability_data["Turn"], 1)
#         self.assertEqual(ability_data["Type"], "Ability")
# 
#     def test_get_hazard_data(self):
#         event = "|-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock"
#         turn = MockTurn(1, event)
# 
#         self.damage_data.get_damage_data(event, turn)
#         dmg_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(dmg_data["Damage"], 6)
#         self.assertEqual(dmg_data["Dealer"], "Stealth Rock")
#         self.assertEqual(dmg_data["Dealer_Player_Number"], 1)
#         self.assertEqual(dmg_data["Source_Name"], "Stealth Rock")
#         self.assertEqual(dmg_data["Receiver"], "Ferrothorn")
#         self.assertEqual(dmg_data["Receiver_Player_Number"], 2)
#         self.assertEqual(dmg_data["Turn"], 1)
#         self.assertEqual(dmg_data["Type"], "Hazard")
# 
#     def test_get_status_data(self):
#         event = "|-damage|p1a: Rillaboom|94/100 tox|[from] psn"
#         turn = MockTurn(1, event)
# 
#         self.damage_data.get_damage_data(event, turn)
#         dmg_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(dmg_data["Damage"], 6)
#         self.assertEqual(dmg_data["Dealer"], "tox")
#         self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
#         self.assertEqual(dmg_data["Source_Name"], "tox")
#         self.assertEqual(dmg_data["Receiver"], "Rillaboom")
#         self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
#         self.assertEqual(dmg_data["Turn"], 1)
#         self.assertEqual(dmg_data["Type"], "Status")
# 
#     def test_get_passive_data(self):
#         event = "|-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn"
#         turn = MockTurn(1, event)
# 
#         self.damage_data.get_damage_data(event, turn)
#         dmg_data = self.damage_data.damage_events[0]
# 
#         self.assertEqual(dmg_data["Damage"], 12)
#         self.assertEqual(dmg_data["Dealer"], "Ferrothorn")
#         self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
#         self.assertEqual(dmg_data["Source_Name"], "Leech Seed")
#         self.assertEqual(dmg_data["Receiver"], "Druddigon")
#         self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
#         self.assertEqual(dmg_data["Turn"], 1)
#         self.assertEqual(dmg_data["Type"], "Passive")
# 
# 
# if __name__ == "__main__":
#     unittest.main()
