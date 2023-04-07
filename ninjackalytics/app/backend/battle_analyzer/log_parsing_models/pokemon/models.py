import re
from typing import List, Dict, Tuple


class BattlePokemon:
    def __init__(self, battle: object):
        self.log = battle.get_log()
        self.pokemon = PokemonFinder(self.log).get_pokemon()
        self.teams = self._create_teams()

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


class Team:
    def __init__(self, pokemon: list):
        self.pokemon = pokemon


class Pokemon:
    def __init__(
        self, real_name: str, nickname: str, player_num: str, hp=100, hp_change=None
    ):
        self.real_name = self._handle_real_name(real_name)
        self.nickname = nickname
        self.player_num = int(player_num)
        self.hp = hp
        self.hp_change = hp_change

    def _handle_real_name(self, real_name: str) -> str:
        """
        Returns a str with the real name of the pokemon before the first
        comma

        Parameters
        ----------
        real_name : str
            The real name of the pokemon

        Returns
        -------
        str
            The real name of the pokemon before the first comma

        """
        return real_name.split(",")[0]

    def __hash__(self):
        return hash((self.real_name, self.player_num))

    def __eq__(self, other: object):
        """
        Defines how a Pokemon object is considered equal to another Pokemon object

        When the real_name and player_num of the two Pokemon objects are the same then the
        objects are considered equal
        """
        return (
            self.__class__ == other.__class__
            and self.real_name == other.real_name
            and self.player_num == other.player_num
        )

    def update_hp(self, new_hp: float) -> None:
        """
        Updates the hp_change and hp stat of the object

        Parameters
        ----------
        new_hp : float
            A float that represents the new hp of the Pokemon
        """
        self.hp_change = new_hp - self.hp
        self.hp = new_hp

    @property
    def get_hp(self):
        return self.hp

    @property
    def get_hp_change(self) -> float:
        return self.hp_change

    def check_if_name_is_self(self, name: str) -> bool:
        """
        Checks a provided raw_name and returns True if it refers to self and False if it does not.

        Paramters
        ---------
        name : str
            The raw name found in the log

        Returns
        -------
        bool
            True if the provided raw_name refers to self and False if it does not.

        Example:
        name = p1a: Espeon
        prefix = the p1[a-d] part (== "p1a" here)
        player_num = prefix[1], i.e. the second character of the prefix, here 1
        """
        prefix = re.findall("[p][1-2][a-d]: ", name)[0]
        player_num = int(prefix[1])
        name = name.split(prefix)[1]

        if player_num == self.player_num and name == self.nickname:
            return True
        else:
            return False


class PokemonFinder:
    def __init__(self, log: str):
        """
        Initialize PokemonFinder object.

        Parameters
        ----------
        log : str
            The battle log string to extract Pokemon data from.
        """
        self.log = log

    def get_pokemon(self) -> list:
        """
        Extract and return a list of Pokemon objects found in the log.

        Returns
        -------
        list
            A list of Pokemon objects
        """
        preview_mons = self._extract_previews(self.log)
        entrance_mons = self._extract_entrances(self.log)
        pokemon_parameters = self._create_pokemon_parameters(
            preview_mons + entrance_mons
        )
        mons = self._create_pokemon_objects(pokemon_parameters)
        return self._remove_duplicates(mons)

    def _extract_previews(self, battle_log: str) -> list:
        """
        Extract and return a list of Pokemon data from the log preview.

        Parameters
        ----------
        battle_log : str
            The battle log string to extract Pokemon data from.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name and player number of a
            Pokemon.
        """
        try:
            preview = battle_log.split("|gen")[1].split("|start")[0]
            team_preview_pattern = (
                r"p(?P<player_num>[1-4]+)" + r"\|(?P<real_name>[A-z| |-]+[^,|\-*|\n])"
            )
            return [
                match.groupdict()
                for match in re.finditer(team_preview_pattern, preview)
            ]
        except IndexError:
            return []

    def _extract_entrances(self, battle_log: str) -> list:
        """
        Extract and return a list of Pokemon data from the log entrances.

        Parameters
        ----------
        battle_log : str
            The battle log string to extract Pokemon data from.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name, nickname, and
            player number of a Pokemon.
        """
        pattern = (
            r"p(?P<player_num>[1-4]){1}[a-c]{1}: "
            + r"(?P<nickname>.*)\|"
            + r"(?P<real_name>[A-Z]+[a-z]+.+)\|[0-9]+\/[0-9]+"
        )
        return [match.groupdict() for match in re.finditer(pattern, battle_log)]

    def _create_pokemon_parameters(self, pokemon_found: list) -> list:
        """
        Extract and return a list of dictionaries containing Pokemon parameters.

        Parameters
        ----------
        pokemon_found : list
            A list of dictionaries containing the real name, nickname, and player number of a Pokemon.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name, nickname, and player number of a Pokemon.
        """
        return [
            {
                "real_name": match.get("real_name"),
                "nickname": match.get("real_name"),
                "player_num": match.get("player_num"),
            }
            if not match.get("nickname")
            else match
            for match in pokemon_found
        ]

    def _create_pokemon_objects(self, pokemon_params: list) -> dict:
        """
        Create and return a dictionary of Pokemon objects.

        Parameters
        ----------
        pokemon_object_params : list
            A list of dictionaries containing Pokemon parameters.

        Returns
        -------
            A list of Pokemon objects
        """
        return [Pokemon(**pokemon_param) for pokemon_param in pokemon_params]

    def _remove_duplicates(self, mons: list) -> list:
        """
        Return a list of unique Pokemon objects - giving priority to those with nicknames

        Paramters
        ---------
        mons : list
            A list of all Pokemon objects found - even duplicates found in the team preview and in the
            entrances.

        Returns
        -------
            A list of unique Pokemon objects
        """
        nicknamed_mons = [mon for mon in mons if mon.nickname != mon.real_name]
        other_mons = [mon for mon in mons if mon not in nicknamed_mons]

        nicknamed_mons = list(set(nicknamed_mons))  # ensure no duplicates exist
        other_mons = list(set(other_mons))  # ensure no duplicates exist

        unique_mons = nicknamed_mons + other_mons

        return unique_mons
