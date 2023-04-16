import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.log_models.turn import Turn


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
