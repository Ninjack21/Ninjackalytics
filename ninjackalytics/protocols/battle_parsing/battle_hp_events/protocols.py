from typing import Dict, List, Tuple, Protocol


class HealData(Protocol):
    def get_heal_data(self, event: str, turn: Turn) -> None:
        ...


class DamageData(Protocol):
    def get_damage_data(self, event: str, turn: Turn) -> None:
        ...
