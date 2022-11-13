from poke_stats_gen_backend.High_Level.Session import Session
from poke_stats_gen_backend.models import *
from Backend.config import REPLAY_URL
from Auto_Pull_Replays.Config import ERROR_RETURN_DIC
from inspect import getmembers, isfunction, isclass


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
            print(f"\n\nadd the following to the error db:\n{error_info}\n\n")
            update_error_db(error_info)

            return_dic = {"Battle_ID": info_dic["Table_ID"], "Turn": turn}
            return_info = trim_error_return_dic(name, return_dic)
            return return_info

    return wrapper


def trim_error_return_dic(name, return_dic):
    import poke_stats_gen_backend.Action.General_Functions as action
    import poke_stats_gen_backend.Damage_and_Heal.Damage_Functions as dmg
    import poke_stats_gen_backend.Damage_and_Heal.Misc_Functions as msc
    import poke_stats_gen_backend.Damage_and_Heal.Healing_Functions as heal
    import poke_stats_gen_backend.Switch.General_Functions as switch
    from poke_stats_gen_backend.models import damages, healing, pivots, actions

    all_funcs = {
        "action_functions": getmembers(action, isfunction),
        "dmg_functions": getmembers(dmg, isfunction),
        "msc_functions": getmembers(msc, isfunction),
        "heal_functions": getmembers(heal, isfunction),
        "switch_functions": getmembers(switch, isfunction),
    }

    funcs_mapping = {
        "action_functions": actions,
        "dmg_functions": damages,
        "msc_functions": damages,
        "heal_functions": healing,
        "switch_functions": pivots,
    }

    error_func_type = "?"
    for func_type in all_funcs:
        for func in all_funcs[func_type]:
            current_func_name = func[0]
            if current_func_name == name:
                error_func_type = func_type

    error_table_attributes = dir(funcs_mapping[error_func_type])
    error_table_attributes = [
        attribute
        for attribute in error_table_attributes
        if attribute in ERROR_RETURN_DIC
    ]

    for attribute in error_table_attributes:
        return_dic[attribute] = ERROR_RETURN_DIC[attribute]

    return return_dic
