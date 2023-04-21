import re
from typing import Dict, Tuple, Optional

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


class RegeneratorHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(
        self, event: str, turn: Turn, battle=None
    ) -> Optional[Dict[str, str]]:
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
