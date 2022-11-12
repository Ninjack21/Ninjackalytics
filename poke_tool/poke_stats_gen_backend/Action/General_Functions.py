import re
from poke_stats_gen_backend.Errors.Error_Handling import handle_errors


def is_line_significant(line):
    if "|switch|" in line.line or "|move|" in line.line:
        return True
    else:
        return False


@handle_errors
def get_line_action_info(info_dic, battle_info_dic):
    turn = info_dic["turn"]
    battle_table_id = battle_info_dic["Table_ID"]
    p1_action_dic = {
        "Turn": turn.number,
        "Battle_ID": battle_table_id,
        "Player_Number": 1,
    }
    p2_action_dic = {
        "Turn": turn.number,
        "Battle_ID": battle_table_id,
        "Player_Number": 2,
    }

    actions_dic = {}

    pattern = r"(\|switch\|p[1-4]|\|move\|p[1-4])+"
    turn_info = re.findall(pattern, turn.turn)

    p1_turn_actions = [action for action in turn_info if "p1" in str(action)]
    p2_turn_actions = [action for action in turn_info if "p2" in str(action)]

    # ------------------ Player 1 ------------------
    if len(p1_turn_actions) != 0:
        p1_action_dic["Action"] = p1_turn_actions[0].split("|")[1]  # |action|p#
    else:
        p1_action_dic["Action"] = "incapacitated"

    # ------------------ Player 2 ------------------
    if len(p2_turn_actions) != 0:
        p2_action_dic["Action"] = p2_turn_actions[0].split("|")[1]  # |action|p#
    else:
        p2_action_dic["Action"] = "incapacitated"

    actions_dic["P1"] = p1_action_dic
    actions_dic["P2"] = p2_action_dic

    return actions_dic
