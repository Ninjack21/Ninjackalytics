import re
from typing import Dict, List, Tuple, Protocol

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)


# ============= START PROTOCOLS =============
class Turn(Protocol):
    number: int
    text: str


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...


class BattlePokemon(Protocol):
    def get_pnum_and_name(self) -> Tuple[int, str]:
        ...

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        ...

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        ...

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        ...


# ============= END PROTOCOLS =============


class HealData:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        self.battle = battle
        self.move_data_finder = MoveDataFinder(battle_pokemon)
        self.passive_data_finder = PassiveDataFinder(battle_pokemon)
        self.item_ability_data_finder = ItemAbilityDataFinder(battle_pokemon)
        self.source_routing = {
            "move": self.move_data_finder,
            "passive": self.passive_data_finder,
            "item": self.item_ability_data_finder,
            "ability": self.item_ability_data_finder,
        }

    def get_heal_data(self, event: str, turn: Turn) -> Dict[str, str]:
        """
        Get the heal data from an event.

        Parameters:
        -----------
        event: str
            - The event
        turn: Turn
            - The turn the event occurred on.

        Returns:
        --------
        Dict[str, str]:
            - The heal data from the event.
        ---
        """

        source_type = self._get_source_type(event)
        source_data_finder = self._get_source_data_finder(source_type)
        heal_dict = source_data_finder.get_heal_data(event, turn, self.battle)

        return heal_dict

    def _get_source_type(self, event: str) -> str:
        """
        Determines the source type of the heal.

        Parameters
        ----------
        event : str
            - The event where a |-heal| was seen.

        Returns
        -------
        str
            - One of the following:
                - move
                - passive
                - item
                - ability
                - drain move
                - terrain

        example_events
        --------------
        item : |-heal|p2a: Garchomp|100/100|[from] item: Leftovers
        ability : |-heal|p2a: Avalugg|100/100|[from] ability: Ice Body
        move : |-heal|p2a: Moltres|100/100
        drain move : |-heal|p2a: Venusaur|100/100|[from] drain: Giga Drain
        passive : |-heal|p2a: Garchomp|100/100|[silent]
        terrain : |-heal|p2a: Garchomp|100/100|[from] terrain: Grassy Terrain
        ---
        """
        # TODO: need to change line_parts aspect of this
        if "[silent]" in line_parts[3]:
            heal_type = "passive"
        elif "item:" in line_parts[3]:
            heal_type = "item"
        elif "ability:" in line_parts[3]:
            heal_type = "ability"
        elif "move:" in line_parts[3]:
            heal_type = "move"  # this means delayed heal like wish
        elif "drain" in line_parts[3]:
            heal_type = "drain move"
        elif "Terrain" in line_parts[3]:
            heal_type = "terrain"
        else:
            heal_type = "passive"  # this indicates something like aqua ring
        return heal_type

    def _get_source_data_finder(self, source_type: str) -> DamageDataFinder:
        return self.source_routing[source_type]
