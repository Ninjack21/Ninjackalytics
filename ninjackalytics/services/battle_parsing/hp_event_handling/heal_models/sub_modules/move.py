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


class MoveHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_heal_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        heal_regex = re.compile(
            r"\|-heal\|(?P<raw_name>.+?)\|(?P<new_hp>\d+?/\d+)(?:(?P<source_info>.*))"
        )
        match = heal_regex.match(event)

        if match:
            raw_name = match.group("raw_name")
            pnum, name = self.battle_pokemon.get_pnum_and_name(raw_name)
            hp_change = self._get_hp_change(event, raw_name)

            source_name = self._find_move_heal_source(turn.text, pnum)

            heal_dict = {
                "Healing": hp_change,
                "Receiver": name,
                "Receiver_Player_Number": pnum,
                "Source_Name": source_name,
                "Turn": turn.number,
                "Type": "Move",
            }
            return heal_dict
        else:
            return None

    def _find_move_heal_source(self, turn_text: str, receiver_pnum: int) -> str:
        """
        Searches for 2 types of move heal events. The first is the normal move heal event like
        roost or recover. The second is a move heal event that is delayed and comes from a move
        like wish. The second type of event is identified by the [from] move: keyword.

        Parameters
        ----------
        turn_text : str
            - The text of the turn where the heal event is found.

        receiver_pnum : int
            - The player number of the pokemon that is receiving the heal.

        Returns
        -------
        str
            - The name of the move that caused the heal. If it does not find one, simply returns
            "Unknown Source".
        """
        delayed_heal_regex = re.compile(
            r"\|-heal\|.+?\|.+?\|\[from\] move: (?P<move_name>.+)\|"
        )
        delayed_match = delayed_heal_regex.search(turn_text)

        self_heal_move_pattern = (
            f"\|move\|p{receiver_pnum}.: .*\|(?P<move>.*)\|p{receiver_pnum}.: .*"
        )
        normal_heal_regex = re.compile(self_heal_move_pattern)
        normal_match = normal_heal_regex.search(turn_text)

        if delayed_match:
            return delayed_match.group("move_name")
        elif normal_match:
            return normal_match.group("move")
        else:
            return "Unknown Source"
