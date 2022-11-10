from poke_tool.Auto_Pull_Replays.Session import Session
from poke_tool.poke_stats_gen_backend.models import errors
from poke_tool.Backend.config import REPLAY_URL
import inspect


def update_error_db(error_info):
    Error = errors(**error_info)
    with Session.begin() as session:
        exists = session.query(errors.id).filter_by(Battle_URL=Error.Battle_URL).first()
        if not exists:
            session.add(Error)


def handle_errors(f):
    name = f.__name__

    def wrapper(*args, **kwargs):
        try:
            return_info = f(*args, **kwargs)
            return return_info
        except Exception as error:
            bid = kwargs["info_dic"][
                "Battle_ID"
            ]  # all info_dic's will have bid for errors
            turn = kwargs["info_dic"]["turn"].number
            error_info = {
                "Battle_URL": f"{REPLAY_URL}{bid}",
                "Function_Name": name,
                "Error_Message": error,
                "Turn": turn,
            }
            print(error_info)
            update_error_db(error_info)
            return wrapper
