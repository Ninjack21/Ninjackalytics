import re


def faint_info(info_dic):
    line = info_dic["line"]
    turn = info_dic["turn"]
    mons = info_dic["mons"]
    line_pattern = (
        "[^\|]+"  # this breaks out a line into it's key parts by "|" dividers
    )
    fnt_line = re.findall(line_pattern, line.line)

    mon_of_interest = fnt_line[1]
    prefix = re.findall("[p][1-2][a-d]: ", mon_of_interest)[0]
    mon_of_interest_key_name = (
        prefix.replace("a:", "").replace("b:", "") + mon_of_interest.split(prefix)[1]
    )
    mon_obj = mons[mon_of_interest_key_name]

    new_hp = 0
    if mon_obj.hp != new_hp:
        mon_obj.update_hp(new_hp)
        faint_info_dic = {
            "Damage": abs(mon_obj.get_hp_change),
            "Dealer": mon_obj.battle_name,
            "Source_Name": "Unknown Move",
            "Receiver": mon_obj.battle_name,
            "Turn": turn.number,
            "Type": "KO Effect",
        }
        return faint_info_dic
    else:
        return None
