from .line import Line


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
