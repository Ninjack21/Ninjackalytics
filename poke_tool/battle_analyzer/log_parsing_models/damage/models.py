import re
from typing import Dict, List, Tuple
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


class DamageDataFinder(ABC):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    @abstractmethod
    def get_damage_data(self, event: str, turn: Turn) -> Dict[str, str]:
        ...

    @abstractmethod
    def _get_source_name(self, event: str) -> str:
        ...


class MoveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(
        self, event: str, turn: Turn, battle: Battle
    ) -> List[Dict[str, str]]:
        pass

    def _get_source_name(self, event: str) -> str:
        pass


class ItemOrAbilityDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(
        self,
        event: str,
        turn: Turn,
    ) -> List[Dict[str, str]]:
        damage_data_list = []
        for turn in self.battle.get_turns():
            # Extract switch events from turn text
            damage_events = re.findall(r"\|-damage.*", turn.text)
            for event in events:
                damage_source = self._get_damage_source(event)
                if damage_source == "item" or damage_source == "ability":
                    damage_data_list.append(
                        self._extract_item_or_ability_info(turn, event)
                    )
        return damage_data_list

    def _get_source_name(self, event: str) -> str:
        pass

    def _extract_item_or_ability_info(self, turn: Turn, event: str) -> Dict[str, str]:
        item_or_ability_info_dic = {}

        receiver = self._get_receiver(event)
        item_or_ability_info_dic["Receiver"] = receiver[1]

        source_name = self._get_source_name_from_event(event)
        item_or_ability_info_dic["Source_Name"] = source_name

        dealer = self._get_dealer(event)
        item_or_ability_info_dic["Dealer"] = dealer[1]

        hp_change = self._get_hp_change(event, receiver)
        item_or_ability_info_dic["Damage"] = abs(hp_change)

        item_or_ability_info_dic["Type"] = self._get_damage_source(event)
        item_or_ability_info_dic["Turn"] = turn.number

        return item_or_ability_info_dic

    def _get_receiver(self, event: str) -> Tuple[int, str]:
        receiver_raw_name = event.split("|")[2]
        return self.battle_pokemon.get_pnum_and_name(receiver_raw_name)

    def _get_source_name_from_event(self, event: str) -> str:
        line_pattern = (
            "[^\|]+"  # this breaks out a line into its key parts by "|" dividers
        )
        dmg_line = re.findall(line_pattern, event)
        return dmg_line[3].split(": ")[1]

    def _get_dealer(self, event: str) -> Tuple[int, str]:
        line_pattern = (
            "[^\|]+"  # this breaks out a line into its key parts by "|" dividers
        )
        dmg_line = re.findall(line_pattern, event)
        if len(dmg_line) == 5:  # this indicates [of] exists : which tells dealer mon
            dealer_raw_name = dmg_line[4].split("[of] ")[1]
            return self.battle_pokemon.get_pnum_and_name(dealer_raw_name)
        else:  # if no 5th element, then dealer is source name
            return (None, self._get_source_name_from_event(event))

    def _get_hp_change(self, event: str, receiver: Tuple[int, str]) -> float:
        old_hp = self.battle_pokemon.get_pokemon_current_hp(receiver[1])
        new_hp = float(event.split("|")[3].split(" ")[0])
        self.battle_pokemon.update_hp_for_pokemon(receiver[1], new_hp)
        return self.battle_pokemon.get_pokemon_hp_change(receiver[1])


class StatusOrHazardDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(self) -> List[Dict[str, str]]:
        pass

    def _get_source_name(self, event: str) -> str:
        pass


class PassiveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(self) -> List[Dict[str, str]]:
        pass

    def _get_source_name(self, event: str) -> str:
        pass
