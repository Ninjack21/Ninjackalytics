from typing import List, Dict, Tuple
import re
import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]

app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.heal_models.abstract_model import (
    HealDataFinder,
    Turn,
    Battle,
    BattlePokemon,
)


class PassiveHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(self, event: str, turn: Turn, battle=None) -> Dict[str, str]:
        """
        Gets the healing data for a passive heal, which acts as a catch all for unidentified
        types.

        Parameters
        ----------
        event : str
            - The event string where the |-heal| event is found.
        turn : Turn
            - An object containing the text of the turn and the turn number.
        battle : Battle, optional
            - Not needed for PassiveHealData, by default None

        Returns
        -------
        Dict[str, str]
            - A dictionary containing the healing data for a passive heal. Has the following expected
            columns:
                - Healing
                - Receiver
                - Receiver_Player_Number
                - Source_Name
                - Turn
                - Type
        ---
        Example Turn:
        |-damage|p2a: Skarmory|25/100|[from] Leech Seed|[of] p1a: Frosmoth
        |-heal|p1a: Frosmoth|82/100 tox|[silent]
        """
        heal_parts = event.split("|")
        raw_name = heal_parts[2]
        pnum, name = self.battle_pokemon.get_pnum_and_name(raw_name)
        hp_change = self._get_hp_change(event, raw_name)

        source_name = self._find_passive_heal_source(turn, pnum)

        heal_dict = {
            "Healing": hp_change,
            "Receiver": name,
            "Receiver_Player_Number": pnum,
            "Source_Name": source_name,
            "Turn": turn.number,
            "Type": "Passive",
        }
        return heal_dict

    def _find_passive_heal_source(self, turn: Turn, receiver_pnum: int) -> str:
        """
        Handles the logic for finding the source name of a passive heal, otherwise returns
        "Unknown Source".

        Parameters
        ----------
        turn : Turn
            - An object containing the text of the turn and the turn number.
        receiver_pnum : int
            - The player number of the pokemon receiving the heal. Helps to identify the source
            without mistaking an event that happened to the opponent as the source.

        Returns
        -------
        str
            - The name of the source of the passive heal, or "Unknown Source" if the source
            could not be identified.
        ---
        NOTE: This method was built off of a single example and I do not yet know how it will do
        long term. May well need more logic handling to identify different types of passive
        damage sources.
        """
        # can check to see if the opponent took damage [of] receiver
        # ex. |-damage|p2a: Skarmory|25/100|[from] Leech Seed|[of] p1a: Frosmoth
        source_regex = re.compile(
            f"\|-damage\|.+?\|.+?\|\[from\] (.+?)\|\[of\] p{receiver_pnum}"
        )
        match = source_regex.search(turn.text)

        if match:
            return match.group(1)
        else:
            return "Unknown Source"
