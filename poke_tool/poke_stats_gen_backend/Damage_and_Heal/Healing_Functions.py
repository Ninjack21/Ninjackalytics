import re

from poke_tool.poke_stats_gen_backend.High_Level.Global_Functions import (
    get_mon_obj,
)

from poke_tool.poke_stats_gen_backend.Damage_and_Heal.General_Functions import (
    update_mon_hp,
)


def source(info_dic):
    line = info_dic["line"]
    turn = info_dic["turn"]
    turn = turn.turn.split(line.line)[0]
    pattern = "[^\|]+"
    line_parts = re.findall(pattern, line.line)
    if len(line_parts) == 3:
        heal_type = "move"
    else:
        if "[silent]" in line_parts[3]:
            heal_type = "passive"
        elif "item:" in line_parts[3]:
            heal_type = "item"
        elif "ability:" in line_parts[3]:
            heal_type = "ability"
        elif "move:" in line_parts[3]:
            heal_type = "move"  # this means delayed heal like wish
        elif "drain" in line_parts[3]:
            heal_type = "drain move"
        else:
            heal_type = "passive"  # this indicates something like aqua ring
    return heal_type


def check_if_regenerator(info_dic):
    """
    this function simply checks the hp and if it's new updates it and returns True for regenerator healing
    """
    line = info_dic["line"]
    mons = info_dic["mons"]
    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )
    hp_line = re.findall(line_pattern, line.line)

    mon_of_interest = hp_line[1]
    prefix = re.findall("[p][1-2][a-d]: ", mon_of_interest)[0]
    mon_of_interest_key_name = (
        prefix.replace("a:", "").replace("b:", "") + mon_of_interest.split(prefix)[1]
    )
    mon_obj = mons[mon_of_interest_key_name]

    hp_pattern = "\|[0-9]+\/[0-9]+"
    hp_str = re.findall(hp_pattern, line.line)[0]
    hp_frac = hp_str.replace("|", "").split("/")
    new_hp = round((int(hp_frac[0]) / int(hp_frac[1].split(" ")[0])) * 100, 2)

    if new_hp != mon_obj.hp:
        mon_obj.update_hp(new_hp)
        return True
    else:
        return False


def regenerator_healing(info_dic):
    """
    this simply creates the information related to the regenerator healing found (if true from check_hp
    """
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )
    hp_line = re.findall(line_pattern, line.line)

    mon_of_interest = hp_line[1]
    prefix = re.findall("[p][1-2][a-d]: ", mon_of_interest)[0]
    mon_of_interest_key_name = (
        prefix.replace("a:", "").replace("b:", "") + mon_of_interest.split(prefix)[1]
    )
    mon_obj = mons[mon_of_interest_key_name]

    heal_info_dic = {
        "Healing": mon_obj.get_hp_change,
        "Receiver": mon_obj.battle_name,
        "Source_Name": "regenerator",
        "Turn": turn.number,
        "Type": "ability",
    }
    return heal_info_dic


def move_info(info_dic):
    """
    there are 2 forms of heal move:
    1) an immediate heal like roost or slack off which has 3 items in the line
    2) a delayed/secondary heal like wish or giga drain which have more than 3 items in the line
    """
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_info_dic = {}

    line_pattern = "[^\|]+"
    line_info = re.findall(line_pattern, line.line)

    raw_name = line_info[1]
    mon_obj = get_mon_obj(raw_name, mons)
    update_mon_hp(line, mon_obj)

    if len(line_info) == 3:  # this indicates it's an immediate heal move like roost
        move_name_pattern = f"\|move\|{raw_name}\|.*"
        move_name = (
            re.findall(move_name_pattern, turn.turn)[-1]
            .split(f"|{raw_name}|")[1]
            .split("|")[0]
        )

        line_info_dic["Receiver"] = mon_obj.battle_name
        line_info_dic["Healing"] = mon_obj.get_hp_change
        line_info_dic["Source_Name"] = move_name
        line_info_dic["Type"] = "move"
        line_info_dic["Turn"] = turn.number
        return line_info_dic
    else:  # this indicates it's a delayed or secondary effect heal like wish/giga drain
        move_name_pattern = "\|\[from\] .*\|"
        move_name = (
            re.findall(move_name_pattern, line.line)[0]
            .split("[from] ")[1]
            .split("|")[0]
            .replace("move: ", "")
        )

        line_info_dic["Receiver"] = mon_obj.battle_name
        line_info_dic["Healing"] = mon_obj.get_hp_change
        line_info_dic["Source_Name"] = move_name
        line_info_dic["Type"] = "move"
        line_info_dic["Turn"] = turn.number
        return line_info_dic


def item_or_ability_info(info_dic):
    """ """
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_info_dic = {}

    line_pattern = "[^\|]+"
    line_info = re.findall(line_pattern, line.line)

    raw_name = line_info[1]
    mon_obj = get_mon_obj(raw_name, mons)
    update_mon_hp(line, mon_obj)

    heal_source_pattern = "\|\[from\] .*: .*"
    heal_info = re.findall(heal_source_pattern, line.line)[0]
    heal_type = heal_info.split("[from] ")[1].split(":")[0]
    source_name = heal_info.split(": ")[1].split("|")[0]

    line_info_dic["Receiver"] = mon_obj.battle_name
    line_info_dic["Healing"] = mon_obj.get_hp_change
    line_info_dic["Source_Name"] = source_name
    line_info_dic["Type"] = heal_type
    line_info_dic["Turn"] = turn.number
    return line_info_dic


def passive_info(info_dic):
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_info_dic = {}

    line_pattern = "[^\|]+"
    line_info = re.findall(line_pattern, line.line)

    raw_name = line_info[1]
    mon_obj = get_mon_obj(raw_name, mons)
    update_mon_hp(line, mon_obj)

    source_name = (
        line_info[3]
        .replace("[silent]", "reported as: '[silent]'")
        .replace("[from] ", "")
    )

    line_info_dic["Receiver"] = mon_obj.battle_name
    line_info_dic["Healing"] = mon_obj.get_hp_change
    line_info_dic["Source_Name"] = source_name
    line_info_dic["Type"] = "passive"
    line_info_dic["Turn"] = turn.number
    return line_info_dic
