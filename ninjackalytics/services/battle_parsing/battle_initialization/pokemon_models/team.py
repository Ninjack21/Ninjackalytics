import re
from typing import List, Dict, Tuple

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.pokemon_models.pokemon import Pokemon


class Team:
    def __init__(self, pokemon: List[Pokemon]):
        self.pokemon = pokemon

    # TODO: Add some checking to make sure the team is valid
