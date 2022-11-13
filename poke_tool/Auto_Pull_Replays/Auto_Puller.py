from Auto_Pull_Replays.Config import FORMATS, GENERATIONS
from poke_stats_gen_backend.Run_Battle import run_battle
import requests
import time
from datetime import timedelta
from Auto_Pull_Replays.Session import Session
from poke_stats_gen_backend.models import battle_info
from Backend.config import SEARCH_URL, REPLAY_URL


def get_gen_format_replays(gen: str, format: str, page: str):
    url_json = f"{SEARCH_URL}format={gen}{format}&page={page}"
    response = requests.get(url_json).json()
    legit_urls = []  # ignores variations like radicalred
    for battle in response:
        bid = battle["id"]
        with Session.begin() as session:
            exists = session.query(battle_info.id).filter_by(Battle_ID=bid).first()
            if not exists:
                if bid.startswith(f"{gen}{format}"):
                    battle_url = f"{REPLAY_URL}{bid}"
                    legit_urls.append(battle_url)

    return legit_urls


def add_replays_to_database(legit_urls: list):
    success = 0
    failure = 0
    for url in legit_urls:
        try:
            run_battle(url)
            success += 1
        except Exception as error:
            print(f"{url} had the error: {error}")
            failure += 1

    print(
        f"\n\n this batches success rate was {round(float((success / (success + failure))*100))}\n\n"
    )


def auto_runner():
    for gen in GENERATIONS:
        for format in FORMATS:
            more_battles = True
            page_num = 1
            print(f"\n\n----- BEGIN SEARCHING FOR {gen}{format} BATTLES ------\n\n")
            while more_battles:
                legit_urls = get_gen_format_replays(gen, format, page_num)
                if not legit_urls:
                    page_num += 1
                elif page_num == 25:
                    more_battles = False
                else:
                    add_replays_to_database(legit_urls)
                    page_num += 1


def auto_run():
    while True:
        auto_runner()
        delay = timedelta(hours=1)
        time.sleep(
            delay.total_seconds()
        )  # everytime this finishes running let's sleep for 1 hour so more battles can populate
