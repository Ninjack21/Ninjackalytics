import re
from typing import List, Tuple
import traceback
from .sub_modules import Pokemon, PokemonFinder, Team


class BattlePokemon:
    def __init__(self, battle: object):
        self.log = battle.get_log()
        try:
            self.pokemon = PokemonFinder(self.log).get_pokemon()
            self.teams = self._create_teams()
            self.error = None
        except Exception as e:
            tb = traceback.format_exc()
            function_with_error = self._find_function_with_error_from_traceback(tb)
            error = {
                "Battle_URL": self.battle.url,
                "Error_Message": str(e),
                "Traceback": tb,
                "Function": function_with_error,
            }
            self.error = error

    def _create_teams(self) -> List:
        """
        Creates a list of the teams in a battle (where team is defined by player numbers)

        Returns
        -------
        list
            A list of the team objects created
        """
        teams = [
            Team([mon for mon in self.pokemon if mon.player_num == num])
            for num in self._find_unique_player_numbers()
        ]
        return teams

    def _find_unique_player_numbers(self) -> List[int]:
        """
        Searches all pokemon objects for unique player numbers. Should almost always be 2, but may
        be some cases where there are more than 2 players.

        Returns
        ------
        list
            list of integers representing the player numbers found
        """
        player_nums = set(mon.player_num for mon in self.pokemon)
        return list(player_nums)

    def get_pnum_and_name(self, raw_name: str) -> Tuple[int, str]:
        """
        Takes a pokemon raw name and returns the player number and name.

        Parameters
        ----------
        raw_name : str
            The name of a pokemon encountered in a battle log

        Returns
        -------
        pnum : int
            The player number of the pokemon
        name : str
            The real_name of the pokemon
        ---
        """
        mon = self.get_mon_obj(raw_name)
        pnum = mon.player_num
        name = mon.real_name
        return pnum, name

    def get_mon_obj(self, raw_name: str) -> object:
        """
        Returns a pokemon object that the raw_name refers to.

        Parameters
        ----------
        raw_name : str
            The name of a pokemon encountered in a battle log

        Returns
        -------
        object
            The pokemon object that the raw_name refers to
        """
        mon = next(
            (mon for mon in self.pokemon if mon.check_if_name_is_self(raw_name)), None
        )
        if not mon:
            raise ValueError(f"Could not find a pokemon named {raw_name}")
        return mon

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        """
        Takes a pokemon raw name and a new hp value and updates the hp for that object.

        Parameters
        ----------
        raw_name : str
            The name of a pokemon encountered in a battle log
        new_hp : float
            The new hp of the pokemon
        """
        mon = self.get_mon_obj(raw_name)
        mon.update_hp(new_hp)

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        """
        Takes a pokemon raw name and returns the hp_change property for the object.

        Parameters
        ----------
        raw_name : str
            The name of a pokemon encountered in a battle log

        Returns
        -------
        hp_change : float
            The float representing the latest change in hp for a pokemon
        """
        mon = self.get_mon_obj(raw_name)
        return mon.get_hp_change

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        """
        Takes a pokemon raw name and returns the hp property for the object, which reflects the current hp.

        Parameters
        ----------
        raw_name : str
            The name of a pokemon encountered in a battle log

        Returns
        -------
        hp : float
            The float representing the current hp for a pokemon
        """
        mon = self.get_mon_obj(raw_name)
        return mon.get_hp

    def _find_function_with_error_from_traceback(self, tb: str) -> str:
        # Regex pattern to match the function name
        pattern = r"\b(?P<function>\w+)\("

        # Find all matches in the traceback
        matches = re.findall(pattern, tb)

        # Regex pattern to match the function name
        pattern = r"\b(?P<function>\w+)\("

        # Find all matches in the traceback
        matches = re.findall(pattern, tb)

        # The function name is the last match that does not contain "Error"
        for match in reversed(matches):
            if "Error" not in match:
                return match

        return None
