import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.log_models.line import Line


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
