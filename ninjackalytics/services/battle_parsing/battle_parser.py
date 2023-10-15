from .battle_data import BattleData
from .battle_data.battle_pokemon import BattlePokemon
from .battle_data.battle import Battle
from .player_choices import ActionData, PivotData
from .hp_event_handling import HpEventsHandler
from .hp_event_handling.damage_models import DamageData
from .hp_event_handling.heal_models import HealData


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

        self.teams = self.battle_pokemon.teams
        self.general_info = battle_info
        self.pivot_info = pivot_info
        self.action_info = action_info
        self.damages_info = damages_info
        self.heals_info = heals_info
