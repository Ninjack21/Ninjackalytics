import re
from datetime import datetime


class BattleData:
    """
    A class for parsing a Pokemon Showdown battle log and extracting information
    for the battle_info table.

    Parameters
    ----------
    battle : object
        A Pokemon Showdown battle object that provides access to the battle log, ID, and format.
    battle_pokemon : object
        A custom object that provides information about the Pokemon used in the battle.

    Attributes
    ----------
    log : str
        The battle log string.
    battle_id : str
        The ID of the battle.
    format : str
        The format of the battle.
    teams_pokemon : list[object]
        The Pokemon used by the players in the battle.

    Methods
    -------
    get_db_info()
        Parses the battle log and returns a dictionary with the following keys:
        - Battle_ID
        - Format
        - P1
        - P2
        - P1_team
        - P2_team
        - Rank
        - Winner
    """

    def __init__(self, battle: object, battle_pokemon: object):
        """
        Constructs a BattleData object with the specified Pokemon Showdown battle
        object and Pokemon object.

        Parameters
        ----------
        battle : object
            A Pokemon Showdown battle object that provides access to the battle log, ID, and format.
        battle_pokemon : object
            A custom object that provides information about the Pokemon used in the battle.
        """
        self.log = battle.get_log()
        self.battle_id = battle.get_id()
        self.format = battle.get_format()
        self.teams_pokemon = battle_pokemon.teams

    def get_db_info(self) -> dict:
        """
        Returns a dictionary with the non-foreign-key columns needed for the battle_info table.

        Returns
        -------
        dict
            A dictionary containing the following keys:
            - Battle_ID
            - Format
            - P1
            - P2
            - Rank
            - Winner
            - Date_Submitted

        Note: As a design choice I decided that the parts dependent on foreign keys would be handled by an
        external class that understands the relationships between the tables. This keeps the requirements of
        the database isolated from this class, whose sole purpose is to find general info from the battle log.
        """
        db_info = self._return_general_info()
        db_info.update(self._parse_player_names())
        db_info.update(self._parse_rank())
        db_info.update(self._parse_winner())

        return db_info

    def _return_general_info(self):
        """
        Returns the general information about the battle.

        Returns
        -------
        dict
            A dictionary containing the Battle_ID, Format, and Date_Submitted keys.
        """
        return {
            "Battle_ID": self.battle_id,
            "Format": self.format,
            "Date_Submitted": datetime.utcnow(),
        }

    def _parse_player_names(self) -> dict:
        """
        Parses the names of the players from the battle log.

        Returns
        -------
        dict
            A dictionary containing the P1 and P2 keys.
        """
        pattern = r"\|player\|p[1-2]{1}\|.*\|"  # Name pattern
        matches = self._findall_regex(pattern)
        p1_name = matches[0].split("|")[3]
        p2_name = matches[1].split("|")[3]
        return {"P1": p1_name, "P2": p2_name}

    def _parse_rank(self) -> dict:
        """
        Parses the rank of the players from the battle log.

        Returns
        -------
        dict
            A dictionary containing the Rank key.

        In the future, I'd like to have a way to indicate if the battle was a tournament or not for rank
        """
        pattern = r"[0-9]{4} &rarr"  # rank pattern
        matches = self._findall_regex(pattern)

        if len(matches) != 0:
            rank1 = matches[0].split(" ")[0]
            rank2 = matches[1].split(" ")[0]
            rank = int(min(rank1, rank2))
        else:
            rank = None
        return {"Rank": rank}

    def _parse_winner(self) -> dict:
        """
        Parses the winner of the battle from the battle log.

        Returns
        -------
        dict
            A dictionary containing the Winner key.
        """
        pattern = r"\|win\|.*"  # winner pattern
        match = self._findall_regex(pattern)
        if match is None:
            winner = "battle resulted in tie"
        else:
            winner = match[0].split("|")[2]

        return {"Winner": winner}

    def _findall_regex(self, pattern: str) -> list:
        """
        Finds all occurrences of a regular expression pattern in the battle log.

        Parameters
        ----------
        pattern : str
            The regular expression pattern to search for.

        Returns
        -------
        list
            A list of strings containing all occurrences of the pattern in the battle log.
        """
        return re.findall(pattern, self.log)
