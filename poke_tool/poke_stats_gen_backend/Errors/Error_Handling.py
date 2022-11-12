from poke_stats_gen_backend.High_Level.Session import Session
from poke_stats_gen_backend.models import errors
from Backend.config import REPLAY_URL


def update_error_db(error_info):
    Error = errors(**error_info)
    with Session.begin() as session:
        exists = session.query(errors.id).filter_by(Battle_URL=Error.Battle_URL).first()
        if not exists:
            session.add(Error)


def handle_errors(f):
    name = f.__name__

    def wrapper(*args, **kwargs):
        info_dic = args[0]  # this assumes that info_dic is always the first argument
        try:
            return_info = f(*args, **kwargs)
            return return_info
        except Exception as error:
            bid = info_dic["Battle_ID"]  # all info_dic's will have bid for errors
            if name == "get_team_info":  # use default turn / line
                turn = 0
                line = "NA"
            else:  # all other funcs use actual turn / line
                turn = info_dic["turn"].number
                line = info_dic["line"].line
            error_info = {
                "Battle_URL": f"{REPLAY_URL}{bid}",
                "Function_Name": name,
                "Error_Message": str(error),
                "Turn": turn,
                "Line": line,
            }
            print(f"add the following to the error db:\n{error_info}\n\n")
            update_error_db(error_info)

    return wrapper
