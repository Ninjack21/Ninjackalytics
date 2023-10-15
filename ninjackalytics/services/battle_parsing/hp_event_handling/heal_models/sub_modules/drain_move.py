from typing import List, Dict, Tuple
import re

from .abstract_model import (
    HealDataFinder,
)

# =================== IMPORT PROTOCOLS ===================
from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Battle,
    BattlePokemon,
    Turn,
)


class DrainMoveHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(self, event: str, turn: Turn, battle=None) -> Dict[str, str]:
        """
        Gets the healing data for a drain move.

        Parameters
        ----------
        event : str
            - The event string where the -|heal| event is found.
        turn : Turn
            - An object containing the text of the turn and the turn number.
        battle : Battle, optional
            - Not needed for DrainMoveData, by default None

        Returns
        -------
        Dict[str, str]
            - A dictionary containing the healing data for a drain move. Has the following expected columns:
                - Healing
                - Receiver
                - Receiver_Player_Number
                - Source_Name
                - Turn
                - Type
        ---
        Example Turn:
        |move|p1a: Abomasnow|Giga Drain|p2a: Torkoal
        |-damage|p2a: Torkoal|60/100
        |-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal
        """
        heal_parts = event.split("|")
        raw_name = heal_parts[2]
        pnum, name = self.battle_pokemon.get_pnum_and_name(raw_name)
        hp_change = self._get_hp_change(event, raw_name)

        source_name = self._find_drain_move(turn, pnum)

        heal_dict = {
            "Healing": hp_change,
            "Receiver": name,
            "Receiver_Player_Number": pnum,
            "Source_Name": source_name,
            "Turn": turn.number,
            "Type": "Drain Move",
        }
        return heal_dict

    def _find_drain_move(self, turn: Turn, receiver_pnum: int) -> str:
        """
        Searches for a drain move in the turn text. If it finds one, it returns the name of the move.
        If it doesn't find one, it returns "Source Not Found".

        Parameters
        ----------
        turn : Turn
            - An object containing the text of the turn and the turn number.

        receiver_pnum : int
            - The player number of the pokemon that is receiving the healing.

        Returns
        -------
        str
            - The name of the drain move if it is found. Otherwise, returns "Source Not Found".

        Example turn text:
        |move|p2a: Torkoal|Should Not Be Me|p1a: Abomasnow
        |move|p1a: Abomasnow|Giga Drain|p2a: Torkoal
        |-damage|p2a: Torkoal|60/100
        |-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal
        |upkeep
        """
        drain_move_regex = re.compile(r"\|move\|(.+?)\|(.+?)\|(.+)")
        matches = drain_move_regex.finditer(turn.text)

        for match in matches:
            raw_name = match.group(1)
            pnum, name = self.battle_pokemon.get_pnum_and_name(raw_name)
            if pnum == receiver_pnum:
                return match.group(2)
        return ""
