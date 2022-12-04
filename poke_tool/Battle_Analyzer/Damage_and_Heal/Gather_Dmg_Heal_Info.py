from . import Damage_Functions as Dmg
from . import Healing_Functions as Heal
from . import Misc_Functions as Msc
from .General_Functions import get_line_significance
from Battle_Analyzer.Models import damages, healing


def get_damage_and_healing_info(response, mons, battle_info_dic, session):
    turns = response.turns
    info_dic = {
        "turns": turns,
        "mons": mons,
        "Battle_ID": battle_info_dic["Battle_ID"],
        "Table_ID": battle_info_dic["Table_ID"],
    }
    for turn_num in turns:
        turn = turns[turn_num]
        info_dic["turn"] = turn
        lines = turn.lines
        for line_num in lines:
            line = lines[line_num]
            info_dic["line"] = line
            sig = get_line_significance(line)
            if not sig:  # first check this and move on if nothing
                continue
            elif sig == "damage":
                dmg_source = Dmg.source(line)
                if dmg_source == "move":
                    line_info_dic = Dmg.move_info(info_dic)
                elif dmg_source == "item" or dmg_source == "ability":
                    line_info_dic = Dmg.item_or_ability_info(info_dic, dmg_source)
                elif (
                    dmg_source == "status"
                    or dmg_source == "hazard"
                    or dmg_source == "passive"
                ):
                    line_info_dic = Dmg.other_info(info_dic, dmg_source)
            elif sig == "faint":
                line_info_dic = Msc.faint_info(info_dic)
            elif sig == "heal":
                heal_type = Heal.source(info_dic)
                if heal_type == "move" or heal_type == "drain move":
                    line_info_dic = Heal.move_info(info_dic)
                elif heal_type == "item" or heal_type == "ability":
                    line_info_dic = Heal.item_or_ability_info(info_dic)
                else:
                    line_info_dic = Heal.passive_info(info_dic)
            elif (
                sig == "check hp"
            ):  # if we triggered sig then check hp must be true by this point - left for rigor
                regenerator = Heal.check_if_regenerator(info_dic)
                if not regenerator:
                    continue
                else:
                    line_info_dic = Heal.regenerator_healing(info_dic)

            # if here, then the line had significance
            if sig in ["damage", "faint"]:
                if line_info_dic:
                    current_line_info = damages(**line_info_dic)
                    session.add(current_line_info)
            else:
                current_line_info = healing(**line_info_dic)
                session.add(current_line_info)
