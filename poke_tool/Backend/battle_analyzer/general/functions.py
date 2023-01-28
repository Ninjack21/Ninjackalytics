import requests
import re
import models


def get_json_response(url: str) -> dict:
    """
    This function tries to get a json response from any url passed to it. If it succeeds, it responds with a true bool and if it fails
    it responds with a false bool
    """
    try:
        response = requests.get(f"{url}.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        raise ValueError(f"An error occurred while trying to access the url")


def extract_entrances(battle_log):
    pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"
    return re.findall(pattern, battle_log)


def get_pokemon(response):
    battle_log = response["log"]
    preview_mons = extract_preview_mons(battle_log)
    prepped_preview_mons = create_pokemon_params_from_preview(preview_mons)
    entrance_mons = extract_entrances(battle_log)
    prepped_entrance_mons = create_pokemon_params_from_entrances(entrance_mons)
    all_prepped_mons = prepped_preview_mons + prepped_entrance_mons
    mons_objects = create_pokemon_objects(all_prepped_mons)
    return mons_objects


def create_pokemon_objects(pokemon_object_params: list) -> object:

    entrance_mons = {}
    for pokemon in pokemon_object_params:
        new_pokemon = models.Pokemon(
            pokemon["real_name"], pokemon["nickname"], pokemon["player_num"]
        )

        entrance_mons[f"p{pokemon['player_num']} {pokemon['nickname']}"] = new_pokemon

    return entrance_mons


def extract_preview_mons(battle_log):
    try:
        preview = battle_log.split("|gen")[1].split("|start")[0]
        team_preview_pattern = r"p[1-4]+\|[A-z| |-]+[^,|\-*|\n]"
        return re.findall(team_preview_pattern, preview)
    except IndexError:
        return []


def create_pokemon_params_from_preview(preview_mons_list):
    pokemon_data = []
    for mons in preview_mons_list:
        split_mons = mons.split("|")
        player_num = split_mons[0][1]
        real_name = split_mons[1]
        nickname = split_mons[1]
        pokemon_data.append(
            {"real_name": real_name, "nickname": nickname, "player_num": player_num}
        )
    return pokemon_data


def create_pokemon_params_from_entrances(entrances):
    params_list = []
    for entrance in entrances:
        params = {}
        split_entrance = entrance.split("|")
        params["player_num"] = split_entrance[0][1]
        params["nickname"] = split_entrance[0][3:].split(":")[-1].strip()
        params["real_name"] = split_entrance[1].split(",")[0]
        params_list.append(params)
    return params_list


# def get_pokemon(response):
#     battle_log = response.log
#     pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"  # Built on regex101.com - finds first time switch in which has form: |switch|p1a: Ampharos|Ampharos, F|360/360

#     entrances = re.findall(pattern, battle_log)

#     entrance_mons = {}

#     for entrance in entrances:
#         name_lookup = entrance.split("|")

#         if not "," in str(name_lookup[1]):
#             real_name = name_lookup[1]
#         else:
#             real_name = name_lookup[1].split(",")[0]

#         if not real_name.endswith("-Mega"):
#             nickname = name_lookup[0][5:]
#             player_num = int(name_lookup[0][1:2])
#             entrance_mons[f"p{player_num} {nickname}"] = models.Pokemon(
#                 real_name, nickname, player_num
#             )  # dict of mons with unique key of pnum nickname

#     preview = battle_log.split("|gen")[1].split("|start")[0]
#     team_preview_pattern = r"p[1-4]+\|[A-z| |-]+[^,|\|\-*]"
#     preview_mons = re.findall(team_preview_pattern, preview)
#     all_mons = entrance_mons

#     if len(preview_mons) != 0:
#         for prev_mon in preview_mons:
#             real_name = prev_mon[3:].split("|")[0].split("-")[0].replace("\n", "")
#             player_num = int(prev_mon[1])
#             battle_name_check = f"p{player_num} {real_name}"

#             exists = False
#             for mon in entrance_mons:
#                 obj = entrance_mons[mon]
#                 if obj.battle_name.startswith(battle_name_check):
#                     exists = True
#             if not exists:
#                 all_mons[battle_name_check] = models.Pokemon(
#                     real_name, real_name, player_num
#                 )  # if we get here then this mon didn't enter battle but we should add it

#     return all_mons


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
