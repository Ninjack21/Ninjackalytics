import requests
import re
from typing import Optional, Iterable


class Battle:
    def __init__(self, url: str):
        """
        Initialize a Battle object from a URL

        Parameters:
        -----------
        url: str
            The URL of the Pokemon battle

        """
        self.url = url
        self.response = Response(self._get_json_response())

    def _get_json_response(self) -> dict:
        """
        Try to get a JSON response from the URL.

        Returns:
        --------
        dict:
            A dictionary containing the JSON response.

        Raises:
        -------
        ValueError:
            If an error occurs while trying to access the URL.
        """
        try:
            response = requests.get(f"{self.url}.json")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            raise ValueError(f"An error occurred while trying to access the URL")

    def get_turn(self, turn_num: int) -> Optional["Turn"]:
        """
        Get the Turn object for the specified turn number.

        Parameters:
        -----------
        turn_num: int
            The turn number for which to retrieve the Turn object.

        Returns:
        --------
        Turn or None:
            The Turn object for the specified turn number, or None if it does not exist.
        """
        try:
            return self.response.turns[turn_num]
        except IndexError:
            return None

    def get_turns(self) -> list():
        """
        Get an iterable of all Turn objects in the battle.

        Returns:
        --------
        Iterable[Turn]:
            An iterable of all Turn objects in the battle.
        """
        return self.response.turns

    def get_id(self) -> str:
        """
        Get the battle ID.

        Returns:
        --------
        str:
            The battle ID.
        """
        return self.response.battle_id

    def get_format(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self.response.format

    def get_log(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self.response.log


class Response:
    def __init__(self, response):
        """
        Initialize a Response object from a JSON response.

        Parameters:
        -----------
        response: dict
            A dictionary containing the JSON response.

        """
        self._log = response["log"]
        self._battle_id = response["id"]
        self._format = response["format"]

        try:
            battle_start = self.log.split("|start\n")[1]
            log_turns = battle_start.split("|turn|")
            self.turns = [
                Turn(turn_num, turn_str) for turn_num, turn_str in enumerate(log_turns)
            ]
        except:
            self.turns = []

    @property
    def battle_id(self) -> str:
        """
        Get the battle ID.

        Returns:
        --------
        str:
            The battle ID.
        """
        return self._battle_id

    @property
    def format(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self._format

    @property
    def log(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self._log


class Turn:
    def __init__(self, turn_num: int, turn_str: str):
        """
        Initialize a Turn object from a turn number and a string containing battle events.
        Only non-comment, non-raw, and non-turn-initialization Lines are created.


        Parameters:
        -----------
        turn_num: int
            The turn number for the Turn object.
        turn_str: str
            A string containing the battle events for the Turn object.

        """
        self.number = turn_num
        self.text = turn_str

        self.lines = [
            Line(line_num, line_str)
            for line_num, line_str in enumerate(self.text.split("\n"), start=1)
            if not line_str.startswith("|c|")
            and not line_str.startswith("|raw|")
            and not "|turn|" in line_str
        ]


class Line:
    def __init__(self, line_num: int, line_str: str):
        """
        Initialize a Line object from a line number and a string containing a single battle event.

        Not sure the Line objects are ever going to do anything besides store data, but have
        object just in case

        Parameters:
        -----------
        line_num: int
            The line number for the Line object.
        line_str: str
            A string containing a single battle event.

        """
        self.text = line_str
        self.number = line_num
