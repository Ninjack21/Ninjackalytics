import re
from typing import Dict, List, Tuple, Protocol, Optional
from abc import ABC, abstractmethod


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


class DamageData:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        self.move_data_finder = MoveDataFinder(battle, battle_pokemon)
        self.passive_data_finder = PassiveDataFinder(battle, battle_pokemon)
        self.item_ability_data_finder = ItemAbilityDataFinder(battle, battle_pokemon)
        self.status_hazard_data_finder = StatusHazardDataFinder(battle, battle_pokemon)

    def _get_damage_source(self, event: str) -> str:
        """
        Get the source of the damage event.

        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The source of the damage event.
        ---
        """
        for source, pattern in self.source_patterns.items():
            if re.search(pattern, event):
                return source

        return "move" if not "[from]" in event else "passive"

    def _get_mon_pnum_and_name(self, raw_name: str) -> Tuple[int, str]:
        """
        Get the player number and name of the Pokemon.

        Parameters:
        -----------
        raw_name: str
            The raw name of the Pokemon.

        Returns:
        --------
        Tuple[int, str]:
            The player number and name of the Pokemon.
        ---
        """
        return self.battle_pokemon.get_pnum_and_name(raw_name)

    def _get_receiver_raw_name(self, event: str) -> str:
        """
        Get the raw name of the Pokemon receiving the damage.

        e.x.
        ============================
        |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox
              ^^^^^^^^^^^^^^^^^^^ (dealer)
        ...
        |-damage|p2a: AMagicalFox|0 fnt <-- expected event
                 ^^^^^^^^^^^^^^^^ (receiver)
        ============================
        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The raw name of the Pokemon receiving the damage.
        ---
        NOTE: This logic is currently the same as _get_dealer_raw_name but separated for rigor
        """
        return event.split("|")[2]

    def _get_dealer_raw_name(self, event: str) -> str:
        """
        Get the raw name of the Pokemon dealing the damage.

        e.x.
        ============================
        |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox <-- expected event
              ^^^^^^^^^^^^^^^^^^^ (dealer)
        ...
        |-damage|p2a: AMagicalFox|0 fnt
                 ^^^^^^^^^^^^^^^^ (receiver)
        ============================

        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The raw name of the Pokemon dealing the damage.
        ---
        """
        return event.split("|")[2]
