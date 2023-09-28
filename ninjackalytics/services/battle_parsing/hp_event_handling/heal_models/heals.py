import re
from typing import Dict, List, Tuple, Protocol

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.heal_models.abstract_model import HealDataFinder
from app.services.battle_parsing.heal_models import (
    AbilityHealData,
    DrainMoveHealData,
    ItemHealData,
    MoveHealData,
    PassiveHealData,
    TerrainHealData,
    RegeneratorHealData,
)


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

        self.source_routing = {
            "move": MoveHealData(battle_pokemon),
            "passive": PassiveHealData(battle_pokemon),
            "item": ItemHealData(battle_pokemon),
            "ability": AbilityHealData(battle_pokemon),
            "drain move": DrainMoveHealData(battle_pokemon),
            "terrain": TerrainHealData(battle_pokemon),
            "regenerator": RegeneratorHealData(battle_pokemon),
        }

        self.heal_data = []

    def get_heal_data(self, event: str, turn: Turn) -> None:
        """
        Gets the heal data when provided with an event str and turn object.

        Parameters
        ----------
        event : str
            - The event where a |-heal| or |switch| was seen.
        turn : Turn
            - A turn object containing the event

        Appends to self.heal_data
        -------------------------
        Dict[str, str]
            - A dictionary with the following keys:
                - Healing
                - Receiver
                - Receiver_Player_Number
                - Source_Name
                - Turn
                - Type
        ---
        """
        source_type = self._get_source_type(event)
        source_data_finder = self._get_source_data_finder(source_type)
        heal_dict = source_data_finder.get_heal_data(event, turn, self.battle)
        if heal_dict:
            self.heal_data.append(heal_dict)

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
        delayed_move : |-heal|p2a: Seismitoad|100/100|[from] move: Wish|[wisher] Clefable
        drain move : |-heal|p2a: Venusaur|100/100|[from] drain: Giga Drain
        passive : |-heal|p2a: Garchomp|100/100|[silent]
        terrain : |-heal|p2a: Garchomp|100/100|[from] terrain: Grassy Terrain
        regenerator : |switch|p2a: Slowbro||100/100
        ---
        """
        line_parts = event.split("|")
        # start with move because it has the shortest length and will cause an IndexError if not first
        if (
            len(line_parts) == 4 and "switch" not in line_parts[1]
        ):  # minimal info = move used, normal len > 4
            heal_type = "move"
        elif "move:" in line_parts[4]:
            heal_type = "move"
        elif "switch" in line_parts[1]:
            heal_type = "regenerator"
        elif "[silent]" in line_parts[4]:
            heal_type = "passive"
        elif "item:" in line_parts[4]:
            heal_type = "item"
        elif "ability:" in line_parts[4]:
            heal_type = "ability"
        elif "drain" in line_parts[4]:
            heal_type = "drain move"
        elif "Terrain" in line_parts[4]:
            heal_type = "terrain"
        else:
            heal_type = "passive"  # this indicates something like aqua ring

        return heal_type

    def _get_source_data_finder(self, source_type: str) -> HealDataFinder:
        return self.source_routing[source_type]
