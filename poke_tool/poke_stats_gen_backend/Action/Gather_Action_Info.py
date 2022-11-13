from poke_stats_gen_backend.High_Level import Classes
from .General_Functions import get_line_action_info
from poke_stats_gen_backend.models import actions


def get_action_info(response, battle_info_dic, session):
    turns = response.turns
    info_dic = {
        "Battle_ID": battle_info_dic["Battle_ID"],
        "Table_ID": battle_info_dic["Table_ID"],
    }
    for turn_num in turns:
        turn = turns[turn_num]
        info_dic["turn"] = turn
        turn_action_dic = get_line_action_info(info_dic)
        for player in turn_action_dic:
            player_action = turn_action_dic[player]
            action = actions(**player_action)
            session.add(action)
