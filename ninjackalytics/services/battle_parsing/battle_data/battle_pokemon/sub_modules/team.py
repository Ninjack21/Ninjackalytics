import re
from typing import List, Dict, Tuple

from . import Pokemon


class Team:
    def __init__(self, pokemon: List[Pokemon]):
        self.pokemon = pokemon

    # TODO: Add some checking to make sure the team is valid
