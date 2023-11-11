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
import traceback
import re


def retry_errors():
    error_retriever = ErrorDataRetriever()
    db_errors = error_retriever.get_errors()
    uploader = BattleDataUploader()
    errors_removed = 0
    errors_changed = 0
    for url in tqdm(db_errors["Battle_URL"].unique()):
        try:
            battle = Battle(url)
            battle_pokemon = BattlePokemon(battle)
            battle_parser = BattleParser(battle, battle_pokemon)
            battle_parser.analyze_battle()
            uploader.upload_battle(battle_parser)
            # Delete row from error database if upload was successful
            session = SessionLocal()
            error = session.query(errors).filter_by(Battle_URL=url).first()
            session.delete(error)
            session.commit()
            session.close()
            errors_removed += 1
        except Exception as e:
            # handle case where there is a new error for this battle. sometimes we may fix the original error
            # but now have a new error to fix
            # first, check if e is the same as the error in the database
            session = SessionLocal()
            error = session.query(errors).filter_by(Battle_URL=url).first()

            if not error.Error_Message == str(e):
                # if the error is different, delete the error and re-run everything to update it
                session.delete(error)
                session.commit()
                session.close()
                # now re-run everything
                try:
                    battle = Battle(url)
                    battle_pokemon = BattlePokemon(battle)
                    battle_parser = BattleParser(battle, battle_pokemon)
                    battle_parser.analyze_battle()
                    # will fail here, but updates db with new error
                    uploader.upload_battle(battle_parser)
                    errors_changed += 1
                except:
                    # continue
                    pass

    print(f"Errors removed: {errors_removed}")
    print(f"Errors changed: {errors_changed}")
