from typing import List, Dict, Tuple, Optional
import re

# ===bring in base objects that don't need changing===
import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
sys.path.insert(1, app_path)
from ninjackalytics.services.battle_parsing.battle_data.battle.sub_modules import (
    Line,
    Turn,
)


class FlexResponse:
    def __init__(
        self,
        battle_id: str,
        format: str,
        *,
        list_turn_tuples: List[Tuple[int, str]] = None,
        list_line_tuples: List[Tuple[int, str]] = None,
    ):
        """
        Parameters
        ----------
        battle_id : str
            - the id of the battle being simulated
        format : str
            - the format of the battle being simulated
        lines : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual line string itself
        turns : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual turn string itself
        """
        self._battle_id = battle_id
        self._format = format

        if list_line_tuples:
            self._log = self._generate_log_from_line_tuples(list_line_tuples)
        if list_turn_tuples:
            self.log = self._generate_log_from_turn_tuples(list_turn_tuples)

        try:
            battle_start = self.log.split("|start\n")[1]
            log_turns = battle_start.split("|turn|")
            self.turns = [
                Turn(turn_num, turn_str) for turn_num, turn_str in enumerate(log_turns)
            ]
        except:
            self.turns = []

    def _generate_log_from_line_tuples(self, lines: List[Tuple[int, str]]):
        """
        Generates a log from a given set of lines of interest. This method will need to take the lines
        and generate turns which contain them. Moreover, it will need to ensure that an appropriate entrance
        is generated for any pokemon seen such that they will be registered by the BattlePokemon object.

        Parameters
        ----------
        lines : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual line string itself

        Returns
        -------
        log : str
            - a generated log object that should satisfy all the requirements expected of the BattleData object that utilizes the
            response object (and thus all subsequently dependent objects which assume a particular interface and internals from the
            battle and battledata objects)
        """
        log = "|start\n"
        # start by generating a turn 0 switch statement for each pokemon found in the lines provided
        # this way they all init at 100 hp without then having their hp reset to 100 upon every subsequent encounter of the
        # pokemon in the log should they appear multiple times
        for _, line in lines:
            log += "|turn|0\n"
            # ex. line -> |move|p1a: Pincurchin|Thunder Wave|p2a: Torterra
            pokemon_found = []
            for section in line.split("|"):
                if (
                    len(re.findall(r"p(?P<player_num>[1-4]){1}[a-c]{1}: ", section))
                    != 0
                ):
                    # generate entrance line that BattlePokemon will recognize
                    # note this system will assume no nicknames are used for testing purposes
                    entrance_line = f"|switch|{section}|100/100\n"
                    log += entrance_line

            # now go through again adding the lines to generated turns
            for num, line in lines:
                # ex. |turn|1
                turn_str = f"|turn|{num}\n"
                log += turn_str
                log += f"{line}\n"
        return log

    def _generate_log_from_turn_tuples(self, turns: List[Tuple[int, str]]):
        """
        Generates a log from a given set of turns of interest. This method will need to take the turns
        and generate an appropriate entrance for any pokemon seen such that they will be registered by the BattlePokemon object.

        Parameters
        ----------
        turns : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual turn string itself

        Returns
        -------
        log : str
            - a generated log object that should satisfy all the requirements expected of the BattleData object that utilizes the
            response object (and thus all subsequently dependent objects which assume a particular interface and internals from the
            battle and battledata objects)
        """
        log = "|start\n"
        # start by generating a turn 0 switch statement for each pokemon found in the turns provided
        # this way they all init at 100 hp without then having their hp reset to 100 upon every subsequent encounter of the
        # pokemon in the log should they appear multiple times
        for _, turn in turns:
            log += "|turn|0\n"
            # ex. turn -> |move|p1a: Pincurchin|Thunder Wave|p2a: Torterra
            pokemon_found = []
            for section in turn.split("|"):
                if (
                    len(re.findall(r"p(?P<player_num>[1-4]){1}[a-c]{1}: ", section))
                    != 0
                ):
                    # generate entrance line that BattlePokemon will recognize
                    # note this system will assume no nicknames are used for testing purposes
                    entrance_line = f"|switch|{section}|100/100\n"
                    log += entrance_line

            # now go through again adding the turns to generated turns
            for num, turn in turns:
                # ex. |turn|1
                log += turn_str
                log += f"{turn}\n"
        return log

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


class FlexBattle:
    def __init__(
        self,
        battle_id: str,
        format: str,
        *,
        list_turn_tuples: List[Tuple[int, str]] = None,
        list_line_tuples: List[Tuple[int, str]] = None,
    ):
        """
        Initialize a Battle object from a specific list of turns or lines for the purpose of testing

        Parameters
        ----------
        battle_id : str
            - the id of the battle being simulated
        format : str
            - the format of the battle being simulated
        lines : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual line string itself
        turns : List[Tuple[int, str]]
            - a list of tuples containing the associated turn number and then the actual turn string itself
        """
        self.url = "I don't expect to show up anywhere..."
        if list_line_tuples:
            self.response = FlexResponse(
                battle_id, format, list_line_tuples=list_line_tuples
            )
        elif list_turn_tuples:
            self.response = FlexResponse(
                battle_id, format, list_turn_tuples=list_turn_tuples
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
