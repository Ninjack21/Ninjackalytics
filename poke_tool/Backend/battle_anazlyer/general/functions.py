import requests
import re
from . import Models


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
        return response

    else:
        return "error"


def get_pokemon(response):
    battle_log = response.log
    pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"  # Built on regex101.com - finds first time switch in which has form: |switch|p1a: Ampharos|Ampharos, F|360/360

    entrances = re.findall(pattern, battle_log)

    entrance_mons = {}

    for entrance in entrances:
        name_lookup = entrance.split("|")

        if not "," in str(name_lookup[1]):
            real_name = name_lookup[1]
        else:
            real_name = name_lookup[1].split(",")[0]

        if not real_name.endswith("-Mega"):
            nickname = name_lookup[0][5:]
            player_num = int(name_lookup[0][1:2])
            entrance_mons[f"p{player_num} {nickname}"] = Models.Pokemon(
                real_name, nickname, player_num
            )  # dict of mons with unique key of pnum nickname

    preview = battle_log.split("|gen")[1].split("|start")[0]
    team_preview_pattern = r"p[1-4]+\|[A-z| |-]+[^,|\|\-*]"
    preview_mons = re.findall(team_preview_pattern, preview)
    all_mons = entrance_mons

    if len(preview_mons) != 0:
        for prev_mon in preview_mons:
            real_name = prev_mon[3:].split("|")[0].split("-")[0].replace("\n", "")
            player_num = int(prev_mon[1])
            battle_name_check = f"p{player_num} {real_name}"

            exists = False
            for mon in entrance_mons:
                obj = entrance_mons[mon]
                if obj.battle_name.startswith(battle_name_check):
                    exists = True
            if not exists:
                all_mons[battle_name_check] = Models.Pokemon(
                    real_name, real_name, player_num
                )  # if we get here then this mon didn't enter battle but we should add it

    return all_mons


def get_mon_obj(raw_name, mons):
    prefix = re.findall("[p][1-2][a-d]: ", raw_name)[0]
    mon_of_interest_key_name = (
        prefix.replace("a:", "").replace("b:", "") + raw_name.split(prefix)[1]
    )
    mon_obj = mons[mon_of_interest_key_name]
    return mon_obj


def get_player_name(mon_obj, response):
    player_preview = response.log.split("gametype")[1].split("|gen")[0]
    player_num = mon_obj.player_num

    player_name_pattern = f"\|p{player_num}\|[^\|]+"
    player_name = re.findall(player_name_pattern, player_preview)[0]

    return player_name
