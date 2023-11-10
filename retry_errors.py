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
                tb = traceback.format_exc()
                function_with_error = _find_function_with_error_from_traceback(tb)
                # if the error is different, update the error in the database
                error.Error_Message = str(e)
                error.Traceback = tb
                error.Function = function_with_error
                session.commit()
                session.close()
                errors_changed += 1

    print(f"Errors removed: {errors_removed}")
    print(f"Errors changed: {errors_changed}")


# copied from battle parser as sometimes the error comes from before the battle parser (i.e. battle pokemon)
# TODO: at some point I should update the design such that battle parser inits battle and battle pokemon
# and if an error occurs in one of these steps the battle parser contains the logic for logging that error
# at the moment, a failure to initialize will not be logged, or, if it is, it will show up incorrectly
def _find_function_with_error_from_traceback(tb: str) -> str:
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
