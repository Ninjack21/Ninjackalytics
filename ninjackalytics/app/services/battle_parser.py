import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing import (
    Battle,
    BattlePokemon,
    ActionData,
    PivotData,
    DamageData,
    HealData,
    BattleData,
)


class BattleParser:
    def __init__(self, url: str):
        # ------ initialize battle parsing models ------
        self.url = url
        self.battle = Battle(url)
        self.battle_pokemon = BattlePokemon(self.battle)
        self.battle_data = BattleData(self.battle, self.battle_pokemon)
        self.action_data = ActionData(self.battle)
        self.pivot_data = PivotData(self.battle, self.battle_pokemon)
        self.damage_data = DamageData(self.battle, self.battle_pokemon)
        self.heal_data = HealData(self.battle, self.battle_pokemon)
        # ------ store battle data for db ------
        self.teams = []
        self.general_info = None
        self.pivot_info = []
        self.action_info = []
        self.damages_info = []
        self.heals_info = []

    def analyze_battle(self) -> None:
        battle_info = self.battle_data.get_db_info()
        pivot_info = self.pivot_data.get_pivot_data()
        action_info = self.action_data.get_action_data()
