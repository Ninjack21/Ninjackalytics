from . import Classes
from poke_stats_gen_backend.High_Level.Global_Functions import (
    get_mon_obj,
)
from poke_stats_gen_backend.Damage_and_Heal.General_Functions import (
    update_mon_hp,
)
import re
from poke_stats_gen_backend.Errors.Error_Handling import handle_errors


def source(line):
    line_str = line.line
    if not "[from]" in line_str:
        return "move"
    elif "[from] item:" in line_str:
        return "item"
    elif "[from] ability:" in line_str:
        return "ability"
    elif Classes.Hazards.check_hazards(line_str):
        return "hazard"
    elif Classes.Statuses.check_statuses(line_str):
        return "status"
    else:
        return "passive"


@handle_errors
def normal_move_info(info_dic, receiver, move_info_dic):
    """
    the normal move info function takes the info_dic, the raw receiver name, and the move_info_dic so it can add the following
    to the move_info_dic by searching for |move|[whatever]|receiver:
    Source Name = Move Name
    Dealer = Dealer real name
    Turn = Turn #
    Type = "move"
    """

    mons = info_dic["mons"]
    turn = info_dic["turn"]

    normal_pattern = f"\|move\|.*\|.*{receiver}"
    move_line = re.findall(normal_pattern, turn.turn)[-1]

    move_name = re.findall("[^\|]+", move_line)[
        2
    ]  # the move_name is always the 3rd thing reported
    move_info_dic["Source_Name"] = move_name

    dealer_raw = move_line.split("|move|")[1].split("|" + move_name)[0]
    dealer_mon_obj = get_mon_obj(dealer_raw, mons)
    move_info_dic["Dealer"] = dealer_mon_obj.battle_name

    move_info_dic["Turn"] = info_dic["turn"].number
    move_info_dic["Type"] = "move"

    return move_info_dic


@handle_errors
def delayed_move_info(info_dic, receiver, move_info_dic):
    """
    the delayed move info funtion takes the info_dic, the raw receiver name, and the move_info_dic so it can add the following
    to the move_info_dic by searching for |-start| to determine what caused |-end|:
    Source Name = Move Name
    Dealer = Dealer real name
    Turn = Turn #
    Type = "move"
    """

    mons = info_dic["mons"]
    turn = info_dic["turn"]
    turns = info_dic["turns"]

    delayed_pattern = "\|-start\|.*"  # note: we could make more explicit, just seems unlikely to be needed

    turn_num = turn.number
    while turn_num > 0:
        turn_obj = turns[turn_num]
        turn_num -= 1

        start_line = re.findall(delayed_pattern, turn_obj.turn)
        if start_line:
            move_line = re.findall("[^\|]+", start_line[0])
            move_name = move_line[2].split("move: ")[1]
            move_info_dic["Source_Name"] = move_name

            dealer_raw = move_line[1]
            dealer_mon_obj = get_mon_obj(dealer_raw, mons)
            move_info_dic["Dealer"] = dealer_mon_obj.battle_name

            move_info_dic["Turn"] = turn.number
            move_info_dic["Type"] = "move"
            return move_info_dic


@handle_errors
def doubles_move_info(info_dic, receiver, move_info_dic):
    """
    the doubles move info function takes the info_dic, the raw receiver name, and the move_info_dic so it can add the following
    to the move_info_dic by searching for either |-anim| or [spread] :
    Source Name = Move Name
    Dealer = Dealer real name
    Turn = Turn #
    Type = "move"

    NOTE: This only takes place in non-single battles - otherwise would trigger delayed_move
    because this is a doubles function, we must also check for spread moves
    """

    mons = info_dic["mons"]
    turn = info_dic["turn"]
    line = info_dic["line"]

    before_dmg_str = turn.turn.split(line.line)[
        0
    ]  # only check info before this (if keyword shows up later in turn, then trigger final else)
    spread_pattern = ".*\[spread\] p[1-2][1-d],p[1-2][1-d].*"
    spread_line = re.findall(spread_pattern, before_dmg_str)

    anim_pattern = "\|-anim\|.*"  # note: we could make more explicit, just seems unlikely to be needed
    anim_line = re.findall(anim_pattern, before_dmg_str)

    if not spread_line:  # if there isn't a spread move, then we must have an anim move

        move_line = re.findall("[^\|]+", anim_line[0])
        move_name = move_line[2]
        move_info_dic["Source_Name"] = move_name

        dealer_raw = move_line[1]
        dealer_mon_obj = get_mon_obj(dealer_raw, mons)
        move_info_dic["Dealer"] = dealer_mon_obj.battle_name

        move_info_dic["Turn"] = turn.number
        move_info_dic["Type"] = "move"

    elif not anim_line:  # if we don't have an anim move then we must have a spread move
        move_line = re.findall("[^\|]+", spread_line[0])
        move_name = move_line[2]
        move_info_dic["Source_Name"] = move_name

        dealer_raw = move_line[1]
        dealer_mon_obj = get_mon_obj(dealer_raw, mons)
        move_info_dic["Dealer"] = dealer_mon_obj.battle_name

        move_info_dic["Turn"] = turn.number
        move_info_dic["Type"] = "move"

    else:  # this means we had both in the same turn and must determine which is the closet to the damage keyword

        spread_len = len(
            before_dmg_str.split(spread_line[0])[1]
        )  # compare the lengths to determine priority
        anim_len = len(before_dmg_str.split(anim_line[0])[1])
        if anim_len < spread_len:  # repeat anim logic, awkward but works for now
            move_line = re.findall("[^\|]+", anim_line[0])
            move_name = move_line[2]
            move_info_dic["Source_Name"] = move_name

            dealer_raw = move_line[1]
            dealer_mon_obj = get_mon_obj(dealer_raw, mons)
            move_info_dic["Dealer"] = dealer_mon_obj.battle_name

            move_info_dic["Turn"] = turn.number
            move_info_dic["Type"] = "move"
        else:  # repeat spread logic
            move_line = re.findall("[^\|]+", spread_line[0])
            move_name = move_line[2]
            move_info_dic["Source_Name"] = move_name

            dealer_raw = move_line[1]
            dealer_mon_obj = get_mon_obj(dealer_raw, mons)
            move_info_dic["Dealer"] = dealer_mon_obj.battle_name

            move_info_dic["Turn"] = turn.number
            move_info_dic["Type"] = "move"

    return move_info_dic


@handle_errors
def doubles_anim_info(info_dic, receiver, move_info_dic):
    mons = info_dic["mons"]
    turn = info_dic["turn"]
    line = info_dic["line"]
    before_dmg_str = turn.turn.split(line.line)[
        0
    ]  # only check info before this (if keyword shows up later in turn, then trigger final else)

    anim_pattern = "\|-anim\|.*"  # note: we could make more explicit, just seems unlikely to be needed
    anim_line = re.findall(anim_pattern, before_dmg_str)

    move_line = re.findall("[^\|]+", anim_line[0])
    move_name = move_line[2]
    move_info_dic["Source_Name"] = move_name

    dealer_raw = move_line[1]
    dealer_mon_obj = get_mon_obj(dealer_raw, mons)
    move_info_dic["Dealer"] = dealer_mon_obj.battle_name

    move_info_dic["Turn"] = turn.number
    move_info_dic["Type"] = "move"

    return move_info_dic


@handle_errors
def move_info(info_dic):
    mons = info_dic["mons"]
    line = info_dic["line"]
    turn = info_dic["turn"]
    move_info_dic = {}

    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )

    receiver = re.findall(line_pattern, line.line)[
        1
    ]  # receiver is always the second part encapsulated in the ||
    rec_mon_obj = get_mon_obj(receiver, mons)
    move_info_dic["Receiver"] = rec_mon_obj.battle_name

    update_mon_hp(line, rec_mon_obj)
    move_info_dic["Damage"] = abs(rec_mon_obj.get_hp_change)

    normal_pattern = f"\|move\|.*\|.*{receiver}"
    move_line = re.findall(normal_pattern, turn.turn)
    if move_line:
        move_info_dic = normal_move_info(info_dic, receiver, move_info_dic)

    elif (
        "-end|" in turn.turn.split(line.line)[0]
    ):  # would need to come before damage keyword
        move_info_dic = delayed_move_info(info_dic, receiver, move_info_dic)

    elif "-anim|" in turn.turn:
        move_info_dic = doubles_anim_info(info_dic, receiver, move_info_dic)

    doubles_move_pattern = "\|move\|[p][1-2][a-d]: .*\|.*"
    doubles_move_line = re.findall(doubles_move_pattern, turn.turn)
    if doubles_move_line and "Source_Name" not in move_info_dic.keys():
        move_info_dic = doubles_move_info(info_dic, receiver, move_info_dic)

    return move_info_dic


@handle_errors
def other_info(info_dic, dmg_source):
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )
    dmg_line = re.findall(line_pattern, line.line)
    status_hazard_info_dic = {}

    receiver = dmg_line[1]
    rec_mon_obj = get_mon_obj(receiver, mons)
    status_hazard_info_dic["Receiver"] = rec_mon_obj.battle_name

    dealer = dmg_line[3].split("[from] ")[1]
    status_hazard_info_dic["Dealer"] = dealer
    status_hazard_info_dic["Source_Name"] = dealer

    update_mon_hp(line, rec_mon_obj)
    status_hazard_info_dic["Damage"] = abs(rec_mon_obj.get_hp_change)

    status_hazard_info_dic["Type"] = dmg_source
    status_hazard_info_dic["Turn"] = turn.number

    return status_hazard_info_dic


@handle_errors
def item_or_ability_info(info_dic, dmg_source):
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )
    dmg_line = re.findall(line_pattern, line.line)
    item_or_ability_info_dic = {}

    receiver = dmg_line[1]
    rec_mon_obj = get_mon_obj(receiver, mons)
    item_or_ability_info_dic["Receiver"] = rec_mon_obj.battle_name

    source_name = dmg_line[3].split(": ")[1]
    item_or_ability_info_dic["Source_Name"] = source_name

    if len(dmg_line) == 5:  # this indicates [of] exists : which tells dealer mon
        dealer = dmg_line[4].split("[of] ")[1]
        dealer_mon_obj = get_mon_obj(dealer, mons)
        item_or_ability_info_dic["Dealer"] = dealer_mon_obj.battle_name
    else:  # if no 5th element, then dealer is source name
        item_or_ability_info_dic["Dealer"] = source_name

    update_mon_hp(line, rec_mon_obj)
    item_or_ability_info_dic["Damage"] = abs(rec_mon_obj.get_hp_change)

    item_or_ability_info_dic["Type"] = dmg_source
    item_or_ability_info_dic["Turn"] = turn.number

    return item_or_ability_info_dic
