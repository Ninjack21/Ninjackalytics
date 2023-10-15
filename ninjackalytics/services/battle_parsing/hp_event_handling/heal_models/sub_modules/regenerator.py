import re
from typing import Dict, Tuple, Optional

from .abstract_model import (
    HealDataFinder,
)

# =================== IMPORT PROTOCOLS ===================
from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Battle,
    BattlePokemon,
    Turn,
)


class RegeneratorHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(
        self, event: str, turn: Turn, battle=None
    ) -> Optional[Dict[str, str]]:
        """
        Gets the healing data for a regenerator related healing event.

        Parameters
        ----------
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
        """
        heal_parts = event.split("|")
        raw_name = heal_parts[2].strip()
        new_hp = float(heal_parts[4].split("/")[0])

        pnum, name = self._get_receiver(event)
        healing = self._get_hp_change(event, raw_name)

        if healing == 0:
            return None

        heal_dict = {
            "Healing": healing,
            "Receiver": name,
            "Receiver_Player_Number": pnum,
            "Source_Name": "Regenerator",
            "Turn": turn.number,
            "Type": "Ability",
        }
        return heal_dict

    def _get_hp_change(self, event: str, receiver_raw_name: str) -> float:
        """
        Parent method has to be overwritten because the event is different for regenerator.
        Example events:
        ---------------
        |switch|p1a: Slowbro|Slowbro, F|90/100
        ---
        """
        # determine new hp in terms of %
        new_raw_hp = event.split("|")[4].split("/")
        # have to split on space for some statuses : |-damage|p1a: Rillaboom|94/100 tox|[from] psn
        new_hp = float(new_raw_hp[0]) / float(new_raw_hp[1].split(" ")[0]) * 100

        self.battle_pokemon.update_hp_for_pokemon(receiver_raw_name, new_hp)
        return self.battle_pokemon.get_pokemon_hp_change(receiver_raw_name)
