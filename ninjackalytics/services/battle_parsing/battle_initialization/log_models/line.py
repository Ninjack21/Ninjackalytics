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
