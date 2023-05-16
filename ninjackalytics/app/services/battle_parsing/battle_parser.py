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
    BattleData,
    HpEventsHandler,
)


class BattleParser:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        # ------ initialize battle parsing models ------
        self.battle = battle
        self.battle_pokemon = battle_pokemon
        self.battle_data = BattleData(self.battle, self.battle_pokemon)
        self.action_data = ActionData(self.battle)
        self.pivot_data = PivotData(self.battle, self.battle_pokemon)
        self.hp_events_handler = HpEventsHandler(self.battle, self.battle_pokemon)
        # ------ store battle data for db ------
        self.teams = []
        self.general_info = None
        self.pivot_info = []
        self.action_info = []
        self.damages_info = []
        self.heals_info = []

    def analyze_battle(self) -> None:
        """
        Directs all of the parsing models to analyze their portions of the battle and then stores the data
        within the BattleParser's attributes that our database model will be able to use.
        """
        battle_info = self.battle_data.get_db_info()
        pivot_info = self.pivot_data.get_pivot_data()
        action_info = self.action_data.get_action_data()
        damages_info = self.damage_data.get_all_damage_data()
        heals_info = self.heal_data.get_all_heal_data()

        self.teams = self.battle_pokemon.teams
        self.general_info = battle_info
        self.pivot_info = pivot_info
        self.action_info = action_info
        self.damages_info = damages_info
        self.heals_info = heals_info
