import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from ninjackalytics.services.database_interactors.battle_data_uploader import (
    BattleDataUploader,
)
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
from ninjackalytics.services.auto_replay_pulls.script import (
    get_battle_urls_selenium,
    get_replay_urls,
)
import traceback
from tqdm import tqdm
import re


def find_function_with_error_from_traceback(tb: str) -> str:
    # Regex pattern to match the function name
    pattern = r"\b(?P<function>\w+)\("

    # Find all matches in the traceback
    matches = re.findall(pattern, tb)

    # Regex pattern to match the function name
    pattern = r"\b(?P<function>\w+)\("

    # Find all matches in the traceback
    matches = re.findall(pattern, tb)

    # The function name is the last match that does not contain "Error"
    for match in reversed(matches):
        if "Error" not in match:
            return match

    return None


# ======= first get all the replay urls =======

try:
    battle_formats = [
        "gen9ou",
        "gen9vgc2024regf",
        "gen9vgc2024regfbo3",
        "gen9vgc2023regulatione",
        "gen9nationaldex",
        "gen9doublesou",
        "gen9ubers",
        "gen9uu",
    ]
    print("prepare to pull URLS...")

    all_urls = []
    for battle_format in tqdm(battle_formats):
        pages = 5
        urls = get_replay_urls(battle_format, pages)
        all_urls.extend(urls)
    print(f"Found {len(all_urls)} urls")
    print("Prepare to begin uploading...")

    # ========= now check the database and find only the ones that are not in the database ========
    ta = TableAccessor()
    battles = ta.get_battle_info()
    battles = battles["Battle_ID"].tolist()
    battles = [f"https://replay.pokemonshowdown.com/{battle}" for battle in battles]
    errors = ta.get_errors()
    errors = errors["Battle_URL"].tolist()

    # only now run the new urls
    all_urls = [url for url in all_urls if url not in battles and url not in errors]
    print(f"Found {len(all_urls)} new urls")
    if len(all_urls) != 0:
        total_errors = 0
        errors_update_threshold = 10
        battle_parsers = []
        uploader = BattleDataUploader()
        for url in tqdm((all_urls), desc="Parsing Battles"):
            try:
                success = False
                tries = 0
                while not success and tries < 5:
                    try:
                        tries += 1
                        battle = Battle(url)
                        success = True
                    except:
                        tries += 1
                        continue
                battle_pokemon = BattlePokemon(battle)
                parser = BattleParser(battle, battle_pokemon)
                parser.analyze_battle()
                uploader.upload_battle(parser)
            except Exception as e:
                total_errors += 1
                tb = traceback.format_exc()
                function = find_function_with_error_from_traceback(tb)
                uploader.upload_error(
                    battle_url=url,
                    error_message=str(e),
                    traceback=tb,
                    function=function,
                )
                if total_errors > errors_update_threshold:
                    print(f"Total Errors: {total_errors}")
                    errors_update_threshold += 10
                continue

        print(f"Total Errors: {total_errors}")
        print(f"Total Error Percentage: {round(total_errors/len(all_urls)*100, 2)}")

except:
    traceback.print_exc()
    print("\n\n-------------Error Occured---------\n\n")
