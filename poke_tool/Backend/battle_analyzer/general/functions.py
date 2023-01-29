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


def get_pokemon(response):
    """
    This function is the main point of the functions seen within it. The goal is to
    parse a battle log and create all of the pokemon objects for each team that can
    be generated.

    We first start with the preview pokemon if there is a team preview. Then we get
    the pokemon discovered in the entrances. In hindsight, this is a poor design as
    those found in the entrances are actually more complete and should overwrite any
    of the pokemon objects created for that pokemon on that team in the team preview.
    The reason for this is the team preview mons do not reveal the nicknames, and thus
    within the actual battle log itself it is less useful to use the team preview mons.
    More work would be required to recognize the pokemon.

    The expected return of this function is a dictionary of all of the mon oobjects where
    the keys are the "battle name" of the pokemon (which is simply the player number and
    then the pokemon nickname - which is always unique).
    """
    battle_log = response["log"]
    preview_mons = extract_preview_mons(battle_log)
    prepped_preview_mons = create_pokemon_params_from_preview(preview_mons)
    entrance_mons = extract_entrances(battle_log)
    prepped_entrance_mons = create_pokemon_params_from_entrances(entrance_mons)
    all_prepped_mons = prepped_preview_mons + prepped_entrance_mons
    mons_objects = create_pokemon_objects(all_prepped_mons)
    return mons_objects


def extract_entrances(battle_log):
    """
    This function holds the regex pattern for finding the entrance of a particular
    pokemon (which allows us to get the nicknames).

    The current design is actually not ideal because, while working, it does not
    work with nicknames that involve characters that are significant to regex (which
    actually includes a lot of nicknames).

    At some point, I will want to update this pattern to use the special named group
    options so that these nicknames (and possibly, in some cases, real pokemon names)
    do not cause this pattern to fail.

    That said, the pattern is built around identifying entrance strings like below:

    (form)
    |switch_keyword|player_identifier: nickname|real_name, gender|current_hp

    (examples)
    |switch|p1a: Valkyrie|Skarmory, F|100/100
    |switch|p2a: Rayo|Zapdos|100/100

    Use https://regex101.com/ to test patterns and see how they will respond.
    """
    pattern = r"p[1-4]{1}[a-c]{1}: .*\|[A-Z]+[a-z]+.*\|[0-9]+\/[0-9]+"
    return re.findall(pattern, battle_log)


def create_pokemon_objects(pokemon_object_params: list) -> object:
    """
    This function is here to take the list of pokemon_object_params and create
    a list of the actual pokemon objects.
    """

    pokemon = {}
    for pokemon_params in pokemon_object_params:
        new_pokemon = models.Pokemon(**pokemon_params)

        pokemon[new_pokemon.battle_name] = new_pokemon

    return pokemon


def extract_preview_mons(battle_log):
    """
    This function is here to handle the extraction of all of the pokemon revealed in a
    team preview.

    Note: not all formats have a team preview, and thus you see the try / except block.
    I except an IndexError, which would result from the preview=battle_log line if there
    is not actually a team preview. If that is the case then one of the splits should
    fail (I forget which). To handle this, we return an empty list so that the rest
    of the code can still run as normal, receiving a list as expected.

    Again, we have the issue where I do not use the group name option in regex but use
    a rigid pattern that, possibly, could get messed up if any significant characters
    to regex are used. I don't think this currently exists, but it may and it certainly
    could in the future.

    The expected team preview form with examples is given below:

    (form)
    |poke_keyword|player_number|real_name, gender|

    (examples)
    |poke|p1|Skarmory, F|
    |poke|p1|Metagross|
    |poke|p1|Heatran, F|
    |poke|p1|Lucario, M|

    Use https://regex101.com/ to test the pattern currently in the code.
    """
    try:
        preview = battle_log.split("|gen")[1].split("|start")[0]
        team_preview_pattern = r"p[1-4]+\|[A-z| |-]+[^,|\-*|\n]"
        return re.findall(team_preview_pattern, preview)
    except IndexError:
        return []


def create_pokemon_params_from_preview(preview_mons_list):
    """
    This function takes in a list of strings that represent pokemon found in a team
    preview, each string containing the data of a single Pokemon, and creates a list of
    dictionaries that contain relevant information about each Pokemon.

    Args:
    - preview_mons_list (list of str): A list of strings where each string represents a
    Pokemon. The format of each string is "pX|real_name" where X is the player number
    and real_name is the name of the Pokemon.

    Returns:
    - list of dict: A list of dictionaries, where each dictionary represents a single
    Pokemon and has the keys "real_name", "nickname", and "player_num".

    Note: in this case, nickname = real_name because team previews do not reveal
    nicknames. This does mean that with the current design of a pokemon object,
    a team preview generated pokemon object is less rigorously defined than one found
    entering a battle, and thus priority should be given to the pokemon objects generated
    from entrances in a battle.
    """
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
    """
    This function takes in a list of strings that represent pokemon found entering a
    battle, each string containing the data of a single Pokemon, and creates a list of
    dictionaries that contain relevant information about each Pokemon.

    Args:
    - preview_mons_list (list of str): A list of strings where each string represents a
    Pokemon. The format of each string is "pX|real_name" where X is the player number
    and real_name is the name of the Pokemon.

    Returns:
    - list of dict: A list of dictionaries, where each dictionary represents a single
    Pokemon and has the keys "real_name", "nickname", and "player_num".
    """
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
