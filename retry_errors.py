from ninjackalytics.services.database_interactors.database_error_retriever import (
    ErrorDataRetriever,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from ninjackalytics.services.database_interactors.battle_data_uploader import (
    BattleDataUploader,
)
from ninjackalytics.database import SessionLocal
from ninjackalytics.database.models.battles import errors
from tqdm import tqdm


def retry_errors():
    error_retriever = ErrorDataRetriever()
    db_errors = error_retriever.get_errors()
    uploader = BattleDataUploader()
    errors_removed = 0
    for url in tqdm(db_errors["Battle_URL"].unique()):
        try:
            battle = Battle(url)
            battle_pokemon = BattlePokemon(battle)
            battle_parser = BattleParser(battle, battle_pokemon)
            battle_parser.analyze_battle()
            uploader.upload_battle(battle_parser)
            print(f"battle {url} was uploaded successfully this time!")
            # Delete row from error database if upload was successful
            session = SessionLocal()
            error = session.query(errors).filter_by(Battle_URL=url).first()
            session.delete(error)
            session.commit()
            session.close()
            print(f"battle {url} was deleted from error database successfully!")
            errors_removed += 1
        except Exception as e:
            continue
    print(f"Errors removed: {errors_removed}")
