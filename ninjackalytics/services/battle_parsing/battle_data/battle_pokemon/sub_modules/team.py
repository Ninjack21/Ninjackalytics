import re
from typing import List, Dict, Tuple

from . import Pokemon


class Team:
    def __init__(self, pokemon: List[Pokemon]):
        self.pokemon = pokemon
        self._verify_mon_names()

    def _verify_mon_names(self):
        for mon in self.pokemon:
            if "|" in mon.real_name or "|" in mon.nickname:
                raise ValueError(
                    f"Pokemon names cannot contain '|' --> Pokemon: real_name: {mon.real_name} | nickname: {mon.nickname}"
                )
