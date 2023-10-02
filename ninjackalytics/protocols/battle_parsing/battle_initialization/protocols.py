from typing import Dict, List, Tuple, Protocol


class Line(Protocol):
    text: str
    number: int


class Turn(Protocol):
    number: int
    text: str
    lines: List[Line]


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...

class BattlePokemon(Protocol):
    def get_pnum_and_name(self) -> Tuple[int, str]:
        ...