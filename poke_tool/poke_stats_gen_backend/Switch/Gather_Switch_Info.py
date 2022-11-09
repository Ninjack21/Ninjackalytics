from poke_tool.poke_stats_gen_backend.Top_Level_Functions import Classes
from .General_Functions import is_line_significant, get_line_switch_info


def get_pivot_info(response, mons):
    turns = response.turns
    info_dic = {"mons": mons}
    for turn_num in turns:
        turn = turns[turn_num]
        info_dic["turn"] = turn
        lines = turn.lines
        for line_num in lines:
            line_info_dic = {}
            line = lines[line_num]
            info_dic["line"] = line
            sig = is_line_significant(line)
            if sig:
                line_info_dic = get_line_switch_info(info_dic, mons)
