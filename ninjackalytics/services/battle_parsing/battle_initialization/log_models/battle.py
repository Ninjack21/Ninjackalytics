import requests
import re
from typing import Optional, List

from . import Response, Turn, Line


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
        except Exception as e:
            raise ValueError(
                f"An error occurred while trying to access the URL\n---\n{e}\n---\n"
            )

    def get_lines(self) -> list:
        """
        Get a list of all Line objects in the battle.

        Returns:
        --------
        List[Line]:
            A list of all Line objects in the battle.
        """
        lines = [
            line
            for turn in self.get_turns()
            for line in turn.lines
            if bool(line.text.strip())
        ]
        return lines

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

    def get_turns(self) -> list:
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
