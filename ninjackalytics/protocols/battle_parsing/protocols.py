from typing import Protocol, List, Dict


class BattleParser(Protocol):
    teams: List[Dict[str, str]]
    general_info: Dict[str, str]
    actions: List[Dict[str, str]]
    damages: List[Dict[str, str]]
    healing: List[Dict[str, str]]
    pivots: List[Dict[str, str]]
