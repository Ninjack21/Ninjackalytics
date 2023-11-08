from ninjackalytics.services.database_interactors.database_error_retriever import (
    ErrorDataRetriever,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from ninjackalytics.services.database_interactors.battle_data_uploader import (
    BattleDataUploader,
)


def retry_errors():
    error_retriever = ErrorDataRetriever()
    errors = error_retriever.get_errors()

    for url in errors["Battle_URL"].unique():
        try:
            battle = Battle(url)
            battle_pokemon = BattlePokemon(battle)
            battle_parser = BattleParser(battle, battle_pokemon)
            battle_parser.analyze_battle()
            uploader.upload_battle(battle_parser)
            print(f"battle {url} was uploaded successfully this time!")
        except Exception as e:
            print(f"battle {url} still had Error: {e}")
            continue
