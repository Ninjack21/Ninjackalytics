from poke_tool.poke_stats_gen_backend.High_Level import Classes
from .General_Functions import is_line_significant, get_line_action_info
from poke_tool.poke_stats_gen_backend.High_Level.Session import Session
from poke_tool.poke_stats_gen_backend.models import actions


def get_action_info(response, battle_info_dic):
    turns = response.turns
    info_dic = {}
    for turn_num in turns:
        turn = turns[turn_num]
        info_dic["turn"] = turn
        turn_action_dic = get_line_action_info(info_dic, battle_info_dic)
        for player in turn_action_dic:
            player_action = turn_action_dic[player]
            print(player_action)
            action = actions(**player_action)
            with Session.begin() as session:
                session.add(action)
