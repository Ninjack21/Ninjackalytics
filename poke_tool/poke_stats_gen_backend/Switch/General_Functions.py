import re
from poke_stats_gen_backend.High_Level.Global_Functions import (
    get_mon_obj,
)
from poke_stats_gen_backend.Errors.Error_Handling import handle_errors


def is_line_significant(line):
    if "|switch|" in line.line:
        return True
    else:
        return False


@handle_errors
def get_line_switch_info(info_dic, mons, battle_info_dic):
    line = info_dic["line"]
    turn = info_dic["turn"]
    line_info_dic = {"Turn": turn.number, "Battle_ID": battle_info_dic["Table_ID"]}

    pattern = r"[^\|]+"
    line_info = re.findall(pattern, line.line)

    mon_enter_raw = line_info[1]
    mon_obj = get_mon_obj(mon_enter_raw, mons)
    line_info_dic["Pokemon_Enter"] = mon_obj.battle_name

    if len(line_info) == 4:  # this indicates action / hard switch
        source_name = "action"
        line_info_dic["Source_Name"] = source_name

    else:  # this indicates move / [from] keyword
        source_name = line_info[4].split(": ")[1].replace("\n", "")
        line_info_dic["Source_Name"] = source_name

    return line_info_dic
