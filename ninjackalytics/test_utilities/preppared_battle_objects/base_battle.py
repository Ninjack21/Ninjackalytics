from typing import Optional


"""
This file is to provide a Response and Battle object for testing purposes. As such we mimic the interface
without requiring the actual connectivity. Over time this battle will become more and more dated. 

It may be good practice to occasionally manually run a more recent battle and then update the tests
accordingly. Though, admittedly, this sounds like a total pain :p

I think instead of that we may want to put a shelf life on all test battles of 5 years. After 5 years
that particular battle and its tests are removed from the testing suite and considered sunset. We should
find enough bugs overtime to continually replenish the test suite with new battles that represent the 
more important features of the game.

Date: 9-28-2023
"""
from ninjackalytics.services.battle_parsing.battle_data.battle.sub_modules.turn import (
    Turn,
)
from ninjackalytics.services.battle_parsing.battle_data.battle.sub_modules.line import (
    Line,
)
from .battle_vars import log, b_id, b_format


class TestResponse:
    def __init__(self, log: str):
        """
        Initialize a Response object from a JSON response.

        Parameters:
        -----------
        response: dict
            A dictionary containing the JSON response.

        """
        self._log = log
        self._battle_id = b_id
        self._format = b_format

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


class TestBattle:
    def __init__(self, log: str = log):
        """
        Initialize a Battle object from a URL

        Parameters:
        -----------
        url: str
            The URL of the Pokemon battle

        """
        self.response = TestResponse(log)

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
