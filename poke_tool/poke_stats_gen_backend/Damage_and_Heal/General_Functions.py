import re


def update_mon_hp(line, mon_obj):
    if not "fnt" in line.line and not "faint" in line.line:
        hp_pattern = "\|[0-9]+\/[0-9]+"
        hp_str = re.findall(hp_pattern, line.line)[0]
        hp_frac = hp_str.replace("|", "").split("/")
        new_hp = round((int(hp_frac[0]) / int(hp_frac[1].split(" ")[0])) * 100, 2)
        mon_obj.update_hp(new_hp)
    else:
        new_hp = 0
        mon_obj.update_hp(new_hp)


def get_line_significance(line):
    """
    this function takes the line object and checks for the 4 things we care about:

    damage_keyword = "|-damage\|"
    faint_keyword = "|faint|"
    heal_keyword = "|-heal|"
    hp_seen_pattern = "[/]\d+"

    It checks in the same order seen above and immediately returns the corresponding direction x_keyword or "check hp" upon success
    """
    damage_keyword = "|-damage|"
    faint_keyword = "|faint|"
    heal_keyword = "|-heal|"
    hp_seen_pattern = "[/]\d+"

    if damage_keyword in line.line:
        return "damage"
    elif faint_keyword in line.line:
        return "faint"
    elif heal_keyword in line.line:
        return "heal"
    elif re.search(hp_seen_pattern, line.line):
        return "check hp"
    else:
        return None
