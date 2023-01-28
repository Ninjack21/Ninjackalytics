import re
from Battle_Analyzer.Battle_Id_Info.Battle_Info import get_bid_info
from Battle_Analyzer.High_Level.Global_Functions import (
    get_response,
    get_pokemon,
)
from Battle_Analyzer.Team.Team_Info import get_team_info
from Battle_Analyzer.High_Level.Models import *
from Battle_Analyzer.Models import *
from Battle_Analyzer.Damage_and_Heal.Gather_Dmg_Heal_Info import (
    get_damage_and_healing_info,
)
from Battle_Analyzer.Action.Gather_Action_Info import get_action_info
from Battle_Analyzer.Switch.Gather_Switch_Info import get_pivot_info
from Battle_Analyzer.High_Level.Session import Session


def run_battle(url):
    # let's later update this to first check if it exists and only then do team info stuff
    response = Response(get_response(url))
    mons = get_pokemon(response)
    info_dic = {"Battle_ID": response.battle_id}
    team_info_dic = get_team_info(info_dic, mons)
    battle_info_dic = get_bid_info(response, team_info_dic)
    if battle_info_dic["Exists"] == False:  # if already exists, backend stops
        with Session.begin() as session:
            get_damage_and_healing_info(response, mons, battle_info_dic, session)
            get_action_info(response, battle_info_dic, session)
            get_pivot_info(response, mons, battle_info_dic, session)
