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


class ItemHealData(HealDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_heal_data(self, event: str, turn: Turn, battle=None) -> Dict[str, str]:
        heal_parts = event.split("|")
        raw_name = heal_parts[2].strip()
        new_hp = float(heal_parts[3].split("/")[0])
        source_name = re.search(r"item: (.+)", heal_parts[4]).group(1)

        pnum, name = self._get_receiver(event)
        healing = self._get_hp_change(event, raw_name)

        heal_dict = {
            "Healing": healing,
            "Receiver": name,
            "Receiver_Player_Number": pnum,
            "Source_Name": source_name,
            "Turn": turn.number,
            "Type": "Item",
        }
        return heal_dict
