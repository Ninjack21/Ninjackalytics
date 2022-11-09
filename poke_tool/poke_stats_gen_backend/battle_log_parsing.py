import re
import requests


def get_response(replay_url) -> bool:
    """
    This function tries to get a json response from any url passed to it. If it succeeds, it responds with a true bool and if it fails
    it responds with a false bool. It adds the battle_id and json response to self if it succeeds and if it fails it adds the user message
    as the response
    """
    url_json = replay_url + ".json"
    response = requests.get(url_json)

    if response.status_code == 200:

        response = response.json()
        battle_id = response["id"]
        return response

    else:
        return "error"


class Response:
    def __init__(self, response):
        self.log = response["log"]
        self.battle_id = response["id"]
        self.format = response["format"]

        battle_start = self.log.split("|start\n")[1]
        log_turns = battle_start.split("|turn|")
        turn_num = 0
        turns = {}
        for turn_str in log_turns:
            turns[turn_num] = Turn(turn_num, turn_str)
            turn_num += 1

        self.turns = turns


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


class BattleLogFunctions:
    @staticmethod
    def get_pokemon(response):
        battle_log = response["log"]
        pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"  # Built on regex101.com - finds first time switch in which has form: |switch|p1a: Ampharos|Ampharos, F|360/360

        entrances = re.findall(pattern, battle_log)

        mons = {}

        for entrance in entrances:
            name_lookup = entrance.split("|")

            if not "," in str(name_lookup[1]):
                real_name = name_lookup[1]
            else:
                real_name = name_lookup[1].split(",")[0]

            if not real_name.endswith("-Mega"):
                nickname = name_lookup[0][5:]
                player_num = int(name_lookup[0][1:2])
                mons[f"p{player_num} {real_name}"] = Pokemon(
                    real_name, nickname, player_num
                )  # dict of mons with unique key of pnum real_name

        return mons

    @staticmethod
    def get_bid_info(response):
        """
        this method takes the stored response dict and adds to the instance properties:

        battle_id
        battle_format
        p1/2_name (as string, not name_id from db)
        rank
        winner (where if tie, winner = 'batttle resulted in tie')
        """
        battle_id = response["id"]
        battle_format = response["formatid"]
        log = response["log"]

        pattern = r"\|player\|p[1-2]{1}\|.*\|"  # Name pattern
        matches = re.findall(pattern, log)
        p1_name = matches[0].split("|")[3]
        p2_name = matches[1].split("|")[3]

        pattern = r"[0-9]{4} &rarr"  # rank pattern
        matches = re.findall(pattern, log)
        if len(matches) != 0:
            rank1 = matches[0].split(" ")[0]
            rank2 = matches[1].split(" ")[0]
            rank = min(rank1, rank2)
        else:
            rank = None

        pattern = r"\|win\|.*"  # winner pattern
        matches = re.search(pattern, log).group()
        if len(matches) == 0:
            winner = "batttle resulted in tie"
        else:
            winner = matches.split("|")[2]

        basic_info = {
            "battle id": battle_id,
            "format": battle_format,
            "p1 name": p1_name,
            "p2 name": p2_name,
            "rank": rank,
            "winner": winner,
        }

        return basic_info


class BattleInfo(
    BattleLogFunctions
):  # note: I have class battle_info for sqlalchemy - lowercase + _ will indicate db connection whereas upper case indicates bat log objects
    def __init__(self, response: dict):
        self.response = response

        basic_info = BattleLogFunctions.get_bid_info(self.response)
        mons = BattleLogFunctions.get_pokemon(self.response)

        self.battle_id = basic_info["battle id"]
        self.format = basic_info["format"]
        self.p1_name = basic_info["p1 name"]
        self.p2_name = basic_info["p2 name"]
        self.rank = basic_info["rank"]
        self.winner = basic_info["winner"]
        self.mons = mons


class Pokemon:
    def __init__(
        self, real_name: str, nickname: str, player_num: int, hp=100, hp_change=None
    ):
        self.real_name = real_name
        self.nickname = nickname
        self.hp = hp
        self.hp_change = hp_change
        self.player_num = player_num

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


class Hazards:
    @staticmethod
    def check_hazards(check_string):
        hazards = ["Stealth Rock", "Spikes", "G-Max Steelsurge"]
        for haz in hazards:
            if haz in check_string:
                return True
        return False


class Statuses:
    @staticmethod
    def check_statuses(check_string):
        statuses = ["psn", "brn"]
        for status in statuses:
            if status in check_string:
                return True
        return False


def get_pokemon(response):
    battle_log = response.log
    pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"  # Built on regex101.com - finds first time switch in which has form: |switch|p1a: Ampharos|Ampharos, F|360/360

    entrances = re.findall(pattern, battle_log)

    mons = {}

    for entrance in entrances:
        name_lookup = entrance.split("|")

        if not "," in str(name_lookup[1]):
            real_name = name_lookup[1]
        else:
            real_name = name_lookup[1].split(",")[0]

        if not real_name.endswith("-Mega"):
            nickname = name_lookup[0][5:]
            player_num = int(name_lookup[0][1:2])
            mons[f"p{player_num} {real_name}"] = Pokemon(
                real_name, nickname, player_num
            )  # dict of mons with unique key of pnum real_name

    return mons


def get_line_significance(line):
    """
    this function takes the line object and checks for the 4 things we care about:

    damage_keyword = "|-damage\|"
    faint_keyword = "|faint|"
    heal_keyword = "|-heal|"
    hp_seen_pattern = "[/]\d+"

    It checks in the same order seen above and immediately returns the corresponding direction x_keyword or "check hp" upon success
    """
    damage_keyword = "|-damage\|"
    faint_keyword = "|faint|"
    heal_keyword = "|-heal|"
    hp_seen_pattern = "[/]\d+"

    if damage_keyword in line.line:
        return "damage"
    elif faint_keyword in line.line:
        return "faint"
    elif heal_keyword in line.line:
        return "heal"
    elif re.search(hp_seen_pattern, line.line).group():
        return "check hp"
    else:
        return None


def get_damage_and_healing_info(response, mons):
    log = response.log
    turns = response.turns
    for turn_num in turns:
        turn = turns[turn_num]
        lines = turn.lines
        for line_num in lines:
            line = lines[line_num]
            sig = get_line_significance(line)
            if not sig:  # first check this and move on if nothing
                continue
            elif sig == "damage":
                pass
            elif sig == "faint":
                # do faint stuff
                pass
            elif sig == "heal":
                # do heal stuff
                pass
            elif sig == "check hp":  # always true by here, left for rigor
                # do regenerator check
                pass


class DmgFunctions:
    @staticmethod
    def dtype(line):
        line_str = line.line
        if not "[from]" in line_str:
            return "move"
        elif "[from] item:" in line_str:
            return "item"
        elif "[from] ability:" in line_str:
            return "ability"
        elif Hazards.check_hazards(line_str):
            return "hazard"
        elif Statuses.check_statuses(line_str):
            return "status"
        else:
            return "unknown"

    @staticmethod
    def dinfo(dtype, line, turn, log):
        if dtype == "move":
            pass
        elif dtype == "item":
            pass
        elif dtype == "ability":
            pass
        elif dtype == "hazard":
            pass
        elif dtype == "status":
            pass
        elif dtype == "unknown":
            pass

    @staticmethod
    def dmove_info(line, turn, log):
        

