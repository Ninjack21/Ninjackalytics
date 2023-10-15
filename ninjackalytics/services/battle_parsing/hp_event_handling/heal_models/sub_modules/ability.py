import re
from typing import Dict, Tuple

from .abstract_model import (
    HealDataFinder,
)

# =================== IMPORT PROTOCOLS ===================
from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Battle,
    BattlePokemon,
    Turn,
)


class AbilityHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(self, event: str, turn: Turn, battle=None) -> Dict[str, str]:
        """
        Gets the healing data for an ability healing.

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
        new_hp = float(heal_parts[3].split("/")[0])
        source_name = re.search(r"ability: (.+)", heal_parts[4]).group(1)

        pnum, name = self._get_receiver(event)
        healing = self._get_hp_change(event, raw_name)

        heal_dict = {
            "Healing": healing,
            "Receiver": name,
            "Receiver_Player_Number": pnum,
            "Source_Name": source_name,
            "Turn": turn.number,
            "Type": "Ability",
        }
        return heal_dict
