class Response:
    def __init__(self, response):
        self.log = response["log"]
        self.battle_id = response["id"]
        self.format = response["format"]

        try:
            battle_start = self.log.split("|start\n")[1]
            log_turns = battle_start.split("|turn|")
            turn_num = 0
            turns = {}
            for turn_str in log_turns:
                turns[turn_num] = Turn(turn_num, turn_str)
                turn_num += 1

            self.turns = turns
        except:  # this means they timed out before selecting a mon at team preview
            self.turns = {}


class Turn:
    def __init__(self, turn_num: int, turn_str: str):
        self.number = turn_num
        self.turn = turn_str

        turn_lines = self.turn.split("\n")
        line_num = 1
        lines = {}
        for line_str in turn_lines:
            if not line_str.startswith("|c|") and not line_str.startswith(
                "|raw|"
            ):  # ignore non-battle lines
                lines[line_num] = Line(line_num, line_str)
                line_num += 1

        self.lines = lines


class Line:
    def __init__(self, line_num: int, line_str: str):
        self.line = line_str
        self.number = line_num


class Pokemon:
    def __init__(
        self, real_name: str, nickname: str, player_num: int, hp=100, hp_change=None
    ):
        self.real_name = real_name
        self.nickname = nickname
        self.hp = hp
        self.hp_change = hp_change
        self.player_num = player_num
        self.battle_name = f"p{self.player_num} {self.real_name}"

    def __hash__(self):
        return hash((self.real_name, self.player_num))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.real_name == other.real_name
            and self.player_num == other.player_num
        )

    def update_hp(self, new_hp):
        self.hp_change = new_hp - self.hp
        self.hp = new_hp

    @property
    def get_hp(self):
        return self.hp

    @property
    def get_hp_change(self):
        return self.hp_change
