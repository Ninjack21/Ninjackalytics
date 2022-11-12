from poke_stats_gen_backend.High_Level import Classes
from .General_Functions import is_line_significant, get_line_switch_info
from poke_stats_gen_backend.models import pivots


def get_pivot_info(response, mons, battle_info_dic, session):
    turns = response.turns
    info_dic = {"mons": mons, "Battle_ID": battle_info_dic["Battle_ID"]}
    for turn_num in turns:
        turn = turns[turn_num]
        info_dic["turn"] = turn
        lines = turn.lines
        for line_num in lines:
            line = lines[line_num]
            info_dic["line"] = line
            sig = is_line_significant(line)
            if sig:
                switch_info = get_line_switch_info(info_dic, mons, battle_info_dic)
                pivot = pivots(**switch_info)
                session.add(pivot)
