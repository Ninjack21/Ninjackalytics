from typing import List, Dict
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

from app.services.battle_parsing.damage_models import DamageData
from app.services.battle_parsing.heal_models import HealData


class BattleParser:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        # ------ initialize battle parsing models ------
        self.battle = battle
        self.battle_pokemon = battle_pokemon
        self.battle_data = BattleData(self.battle, self.battle_pokemon)
        self.action_data = ActionData(self.battle)
        self.pivot_data = PivotData(self.battle, self.battle_pokemon)

        # ------ initialize hp events handler ------
        dmg_data = DamageData(self.battle, self.battle_pokemon)
        heal_data = HealData(self.battle, self.battle_pokemon)
        self.hp_events_handler = HpEventsHandler(self.battle, heal_data, dmg_data)
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
        self.hp_events_handler.handle_events()
        damages_info = self.hp_events_handler.get_damage_events()
        heals_info = self.hp_events_handler.get_heal_events()

        # ------ store battle data for db ------
        self.teams = self._format_teams()
        self.general_info = battle_info
        self.pivot_info = pivot_info
        self.action_info = action_info
        self.damages_info = damages_info
        self.heals_info = heals_info

    def _format_teams(self) -> List[Dict[str, str]]:
        # the other objects are in the format of the dictionary of key words and values
        # the teams in the battle_pokemon object are still objects, though

        teams_list = []
        for team in self.battle_pokemon.teams:
            team_dict = {}
            for i, mon in enumerate(team.pokemon):
                team_dict[f"Pok{i+1}"] = mon.real_name
            teams_list.append(team_dict)

        return teams_list
