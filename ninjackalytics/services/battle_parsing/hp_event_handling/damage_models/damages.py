import re
from typing import Dict, List, Tuple, Protocol


from .sub_modules.d_type_specific_models import (
    DamageDataFinder,
    ItemAbilityDataFinder,
    MoveDataFinder,
    PassiveDataFinder,
    StatusHazardDataFinder,
)

from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Turn,
    Battle,
    BattlePokemon,
)


class DamageData:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        self.battle = battle
        self.move_data_finder = MoveDataFinder(battle_pokemon)
        self.passive_data_finder = PassiveDataFinder(battle_pokemon)
        self.item_ability_data_finder = ItemAbilityDataFinder(battle_pokemon)
        self.status_hazard_data_finder = StatusHazardDataFinder(battle_pokemon)
        self.source_routing = {
            "move": self.move_data_finder,
            "passive": self.passive_data_finder,
            "item": self.item_ability_data_finder,
            "ability": self.item_ability_data_finder,
            "status": self.status_hazard_data_finder,
            "hazard": self.status_hazard_data_finder,
        }
        self.damage_events = []

    def get_damage_data(self, event: str, turn: Turn) -> None:
        """
        Stores an event's data in the self.damage_events list. This is because heals and damages must be done
        simultaneously or the hps of the battle_pokemon will not update properly.

        Parameters:
        -----------
        event: str
            The event
        turn: Turn
            The turn the event occurred on.

        Appends to self.damage_events:
        ------------------------------
        Dict[str, str]
            - A dictionary with the following keys:
                - Damage
                - Dealer
                - Dealer_Player_Number
                - Receiver
                - Receiver_Player_Number
                - Source_Name
                - Type
                - Turn

        Returns:
        --------
        None
        ---
        """

        source_type = self._get_source_type(event)
        source_data_finder = self._get_source_data_finder(source_type)
        damage_dict = source_data_finder.get_damage_data(event, turn, self.battle)

        self.damage_events.append(damage_dict)

    def _get_source_type(self, event: str) -> str:
        if "[from]" not in event:
            return "move"
        elif "[from] item:" in event:
            return "item"
        elif "[from] ability:" in event:
            return "ability"
        elif "[from]" in event:
            # need to check for status, hazard, or passive
            source = event.split("[from] ")[1]
            if source in self.status_hazard_data_finder.statuses:
                return "status"
            elif source in self.status_hazard_data_finder.hazards:
                return "hazard"
            else:
                return "passive"
        else:
            raise Exception("Unknown source type")

    def _get_source_data_finder(self, source_type: str) -> DamageDataFinder:
        return self.source_routing[source_type]
