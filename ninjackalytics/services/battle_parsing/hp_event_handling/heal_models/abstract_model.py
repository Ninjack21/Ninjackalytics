from abc import ABC
from typing import Dict, Protocol, List, Tuple


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


class HealDataFinder(ABC):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        raise NotImplementedError

    def _get_receiver(self, event: str) -> Tuple[int, str]:
        receiver_raw_name = event.split("|")[2]
        return self.battle_pokemon.get_pnum_and_name(receiver_raw_name)

    def _get_hp_change(self, event: str, receiver_raw_name: str) -> float:
        """
        Example events:
        ---------------
        |-damage|p2a: Zapdos|57/100.
        |-damage|p2a: BrainCell|372/424|[from] item: Life Orb
        ---
        """
        # determine new hp in terms of %
        new_raw_hp = event.split("|")[3].split("/")
        # have to split on space for some statuses : |-damage|p1a: Rillaboom|94/100 tox|[from] psn
        new_hp = float(new_raw_hp[0]) / float(new_raw_hp[1].split(" ")[0]) * 100

        self.battle_pokemon.update_hp_for_pokemon(receiver_raw_name, new_hp)
        return self.battle_pokemon.get_pokemon_hp_change(receiver_raw_name)
