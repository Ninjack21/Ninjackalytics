import re
from poke_tool.poke_stats_gen_backend.Top_Level_Functions.Global_Functions import (
    get_mon_obj,
)


def is_line_significant(line):
    if "|switch|" in line.line:
        return True
    else:
        return False


def get_line_switch_info(info_dic, mons):
    line = info_dic["line"]
    turn = info_dic["turn"]
    line_info_dic = {"turn": turn.number}

    pattern = r"[^\|]+"
    line_info = re.findall(pattern, line.line)

    mon_enter_raw = line_info[1]
    mon_obj = get_mon_obj(mon_enter_raw, mons)
    line_info_dic["Pokemon Enter"] = mon_obj.battle_name

    if len(line_info) == 4:  # this indicates action / hard switch
        source_name = "action"
        line_info_dic["Source Name"] = source_name

    else:  # this indicates move / [from] keyword
        source_name = line_info[4].split(": ")[1].replace("\n", "")
        line_info_dic["Source Name"] = source_name

    return line_info_dic
