from doctest import NORMALIZE_WHITESPACE
import re
import requests


class GeneralSearch:
    @staticmethod
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
            response_dict = {
                "Success": True,
                "Response": response,
                "Battle ID": battle_id,
            }
            return response_dict

        else:
            user_msg = (
                "Error = Oops! no response from: "
                + replay_url
                + " - check that you entered it correctly"
            )
            response = user_msg
            response_dict = {"Success": False, "Response": user_msg, "Battle ID": ""}
            return response_dict

    @staticmethod
    def get_pokemon(battle_log):
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


class BattleInfo:  # note: I have class battle_info for sqlalchemy - lowercase will indicate db connection whereas upper case indicates log parsing class
    def __init__(self, response: dict):
        self.response = response
        self.get_bid_info(self)

    def get_bid_info(self):
        """
        this method takes the stored response dict and adds to the instance properties:

        battle_id
        battle_format
        p1/2_name (as string, not name_id from db)
        rank
        winner (where if tie, winner = 'batttle resulted in tie')
        """
        response = self.response
        self.battle_id = response["id"]
        self.battle_format = response["formatid"]
        log = response["log"]

        pattern = r"\|player\|p[1-2]{1}\|.*\|"  # Name pattern
        matches = re.findall(pattern, log)
        self.p1_name = matches[0].split("|")[3]
        self.p2_name = matches[1].split("|")[3]

        pattern = r"[0-9]{4} &rarr"  # rank pattern
        matches = re.findall(pattern, log)
        if len(matches) != 0:
            rank1 = matches[0].split(" ")[0]
            rank2 = matches[1].split(" ")[0]
            self.rank = min(rank1, rank2)
        else:
            self.rank = None

        pattern = r"\|win\|.*"  # winner pattern
        matches = re.search(pattern, log)
        if len(matches) == 0:
            self.winner = "batttle resulted in tie"
        else:
            winner = matches.group()
            self.winner = winner.split("|")[2]


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


class BattleStats:
    def __init__(self, battle_log: str, mons: dict):
        self.battle_log = battle_log
        self.mons = mons

    #  Now we need to iterate line by line in the battle to carefully track hp
    #  We will want to convert all of our current damage and healing info finders to regex expressions for cleaner, more powerful code
