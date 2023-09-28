from typing import List, Protocol
import re


class Turn(Protocol):
    number: int
    text: str


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...

    def get_log(self) -> str:
        ...


class ActionData:
    def __init__(self, battle: Battle):
        self.battle = battle

    def get_action_data(self) -> List[dict]:
        """
        Retuns a list of dictionaries containing the keys:
        - Battle_ID
        - Player_Number
        - Turn
        - Action

        Parameters
        ----------
        battle_id : int
            - An integer representing the battle_info.id from the database

        Returns
        -------
        List[dict]
            - A list of dictionaries containing the above mentioned keys
        """
        players = self._get_player_numbers()
        action_data = [
            {
                "Player_Number": player,
                "Turn": turn.number,
                **self._get_player_action(turn.text, player),
            }
            for player in players
            for turn in self.battle.get_turns()
        ]
        return action_data

    def _get_player_action(self, turn_text: str, player_number: int) -> dict:
        """
        Searches a turn string for a given player's action.

        Parameters
        ----------
        turn_text : str
            - A string containing a turn from the battle log
        player_number : int
            - An integer representing the player number

        Returns
        -------
        dict
            - A dictionary containing the following keys:
                - Player_Number
                - Action
        """
        pattern = (
            r"(\|switch\|p["
            + str(player_number)
            + r"]|\|move\|p["
            + str(player_number)
            + r"])+"
        )

        turn_info = re.findall(pattern, turn_text)

        if not turn_info:
            action = "incapacitated"
        else:
            # e.g. |move|p1a: -> |move|p1a: -> ["", "move", "p1a:""]
            action = turn_info[0].split("|")[1]

        return {"Player_Number": player_number, "Action": action}

    def _get_player_numbers(self) -> List[int]:
        """
        Finds the number of players in the battle. Almost always going to be 2.

        Returns
        -------
        List[int]
            A list of integers representing the player numbers found
        """
        pattern = r"\|p(?P<p_num>[0-9])[A-z]"
        player_numbers = re.findall(pattern, self.battle.get_log())
        player_numbers = [int(x) for x in player_numbers]
        return list(set(player_numbers))
