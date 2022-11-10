import re
from poke_tool.poke_stats_gen_backend.Battle_Id_Info.Battle_Info import get_bid_info
from poke_tool.poke_stats_gen_backend.High_Level.Global_Functions import (
    get_response,
    get_pokemon,
)
from poke_tool.poke_stats_gen_backend.Team.Team_Info import get_team_info
from poke_tool.poke_stats_gen_backend.High_Level.Classes import *
from poke_tool.poke_stats_gen_backend.models import *
from poke_tool.poke_stats_gen_backend.Damage_and_Heal.Gather_Dmg_Heal_Info import (
    get_damage_and_healing_info,
)
from poke_tool.poke_stats_gen_backend.Action.Gather_Action_Info import get_action_info
from poke_tool.poke_stats_gen_backend.Switch.Gather_Switch_Info import get_pivot_info
from poke_tool.poke_stats_gen_backend.High_Level.Session import Session


def run_battle(url):
    response = Response(get_response(url))
    mons = get_pokemon(response)
    info_dic = {"Battle_ID": response.battle_id}
    team_info_dic = get_team_info(mons, info_dic)
    battle_info_dic = get_bid_info(response, team_info_dic)
    if battle_info_dic["Exists"] == False:  # if already exists, backend stops
        with Session.begin() as session:
            get_damage_and_healing_info(response, mons, battle_info_dic, session)
            get_action_info(response, battle_info_dic, session)
            get_pivot_info(response, mons, battle_info_dic, session)
