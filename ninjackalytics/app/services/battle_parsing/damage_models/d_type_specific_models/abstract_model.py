from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Protocol


# =================== DEFINE PROTOCOLS ===================
class BattlePokemon(Protocol):
    def get_pnum_and_name(self) -> Tuple[int, str]:
        ...

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        ...

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        ...

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        ...


class Turn(Protocol):
    number: int
    text: str


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...


# =================== DEFINE MODEL ===================


class DamageDataFinder(ABC):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    @abstractmethod
    def get_damage_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        ...

    @abstractmethod
    def _get_source_name(self, event: str) -> str:
        ...

    def _get_receiver(self, event: str) -> Tuple[int, str]:
        receiver_raw_name = event.split("|")[2]
        return self.battle_pokemon.get_pnum_and_name(receiver_raw_name)

    def _get_hp_change(self, event: str, receiver: str) -> float:
        """
        Example events:
        ---------------
        |-damage|p2a: Zapdos|57/100.
        |-damage|p2a: BrainCell|372/424|[from] item: Life Orb
        ---
        """
        old_hp = self.battle_pokemon.get_pokemon_current_hp(receiver)
        # determine new hp in terms of %
        new_raw_hp = event.split("|")[3].split("/")

        new_hp = self._get_new_hp(new_raw_hp)

        self.battle_pokemon.update_hp_for_pokemon(receiver, new_hp)
        # return the inverse of the hp_change because we want to report damage as positive
        # but the hp_change is negative
        return self.battle_pokemon.get_pokemon_hp_change(receiver) * -1

    def _get_new_hp(self, raw_hp_list: List[str]) -> float:
        """
        Cases:
        Status: |-damage|p1a: Rillaboom|94/100 tox|[from] psn
        Faint: |-damage|p2a: Gardevoir|0 fnt

        Parameters
        ----------
        raw_hp_list : List[str]
            - expects a list of length 1 or 2 (either a faint, 1, or
            a current hp and max hp, 2)

        Returns
        -------
        float
            - The new hp value normalized to a percentage
        """
        if len(raw_hp_list) == 1:
            return 0
        else:
            return float(raw_hp_list[0]) / float(raw_hp_list[1]) * 100
