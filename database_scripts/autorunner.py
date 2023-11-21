import os
import sys

sys.path.append("/Users/jack/Desktop/Ninjackalytics")

os.environ["FLASK_ENV"] = "remote-production"
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from ninjackalytics.services.database_interactors.battle_data_uploader import (
    BattleDataUploader,
)
from ninjackalytics.services.auto_replay_pulls.script import get_replay_urls
from ninjackalytics.database.database import close_tunnel
import traceback
from tqdm import tqdm
from database_scripts import (
    recreate_test_db,
    create_db,
    create_new_tables,
    get_showdown_mon_images,
    retry_errors,
    recalc_metadata_table_info,
    update_pvpmetadata,
)
import subprocess

print("START")
try:
    print("...")
    # Prevent macOS from entering sleep mode
    caffeinate_process = subprocess.Popen(["caffeinate", "-s"])
    print("done.")
    battle_formats = [
        "gen9ou",
        "gen9vgc2023regulatione",
        "gen9nationaldex",
        "gen9doublesou",
        "gen9ubers",
        "gen9nationaldexubers",
        "gen9doublesubers",
        "gen9uu",
        "gen9nationaldexuu",
        "gen9doublesuu",
        "gen9ru",
        "gen9nu",
        "gen9pu",
        "gen9lc",
        "gen9monotype",
        "gen9nationaldexmonotype",
        "gen9cap",
    ]
    print("prepare to pull URLS...")

    all_urls = []
    for battle_format in tqdm(battle_formats):
        pages = 24
        urls = get_replay_urls(battle_format, pages)
        all_urls.extend(urls)
    print(f"Found {len(all_urls)} urls")
    print("Prepare to begin uploading...")
    uploader = BattleDataUploader()

    total_errors = 0
    errors_update_threshold = 10
    for url in tqdm((all_urls)):
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
            if total_errors > errors_update_threshold:
                print(f"Total Errors: {total_errors}")
                errors_update_threshold += 10
            continue

    print(f"Total Errors: {total_errors}")
    print(f"Total Error Percentage: {round(total_errors/len(all_urls)*100, 2)}")

    recalc_metadata_table_info()
    update_pvpmetadata()
    # Allow macOS to enter sleep mode again
    subprocess.run(["killall", "caffeinate"])
except:
    close_tunnel()

close_tunnel()
# Allow macOS to enter sleep mode again
caffeinate_process.run(["killall", "caffeinate"])
