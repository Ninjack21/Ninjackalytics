from poke_stats_gen_backend.High_Level.Session import Session
from poke_stats_gen_backend.models import teams
from poke_stats_gen_backend.Errors.Error_Handling import handle_errors


@handle_errors
def get_team_info(info_dic, mons):
    p1_mon_list = []
    p2_mon_list = []
    for mon in mons:
        mon_obj = mons[mon]
        if mon.startswith("p1"):
            if len(p1_mon_list) == 0:
                p1_mon_list = [mon_obj.real_name]
            else:
                p1_mon_list.append(mon_obj.real_name)
        else:
            if len(p2_mon_list) == 0:
                p2_mon_list = [mon_obj.real_name]
            else:
                p2_mon_list.append(mon_obj.real_name)

    p1_mon_list.sort()
    p2_mon_list.sort()

    p1_team_dic = {}
    p1_filter_by = ""
    i = 1
    for mon in p1_mon_list:
        p1_team_dic[f"Pok{i}"] = mon
        p1_filter_by = p1_filter_by + f"Pok{i}='{mon}',"
        i += 1
    p1_filter_by = p1_filter_by[:-1]

    p2_team_dic = {}
    p2_filter_by = ""
    i = 1
    for mon in p2_mon_list:
        p2_team_dic[f"Pok{i}"] = mon
        p2_filter_by = p2_filter_by + f"Pok{i}='{mon}',"
        i += 1
    p2_filter_by = p2_filter_by[:-1]

    team1 = teams(**p1_team_dic)
    team2 = teams(**p2_team_dic)

    return_dic = {}
    with Session.begin() as session:
        exists1 = session.query(teams.id).filter_by(**p1_team_dic).first()
        exists2 = session.query(teams.id).filter_by(**p2_team_dic).first()

        if not exists1:
            session.add(team1)
            session.flush()
            return_dic["P1_team"] = team1.id
        else:
            return_dic["P1_team"] = exists1.id

        if not exists2:
            session.add(team2)
            session.flush()
            return_dic["P2_team"] = team2.id
        else:
            return_dic["P2_team"] = exists2.id

    return return_dic
