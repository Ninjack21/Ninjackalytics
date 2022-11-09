import re
from poke_tool.poke_stats_gen_backend.models import battle_info
from poke_tool.poke_stats_gen_backend.High_Level.Session import Session


def get_bid_info(response, team_info_dict):
    """
    this method takes the response object and the team_info_dict of pokemon objects
    and adds to the session:

    battle_id
    battle_format
    p1/2_name
    p1/2_team (id)
    rank
    winner (where if tie, winner = 'batttle resulted in tie')
    """
    battle_id = response.battle_id
    battle_format = response.format
    log = response.log

    pattern = r"\|player\|p[1-2]{1}\|.*\|"  # Name pattern
    matches = re.findall(pattern, log)
    p1_name = matches[0].split("|")[3]
    p2_name = matches[1].split("|")[3]

    pattern = r"[0-9]{4} &rarr"  # rank pattern
    matches = re.findall(pattern, log)
    if len(matches) != 0:
        rank1 = matches[0].split(" ")[0]
        rank2 = matches[1].split(" ")[0]
        rank = min(rank1, rank2)
    else:
        rank = None

    pattern = r"\|win\|.*"  # winner pattern
    matches = re.search(pattern, log).group()
    if len(matches) == 0:
        winner = "batttle resulted in tie"
    else:
        winner = matches.split("|")[2]

    basic_info = {
        "Battle_ID": battle_id,
        "Format": battle_format,
        "P1": p1_name,
        "P2": p2_name,
        "P1_team": team_info_dict["P1_team"],
        "P2_team": team_info_dict["P2_team"],
        "Rank": rank,
        "Winner": winner,
    }

    current_battle_info = battle_info(**basic_info)
    return_dict = {"Battle_ID": battle_id}
    with Session.begin() as session:
        exists = session.query(battle_info.id).filter_by(Battle_ID=battle_id).first()
        if not exists:
            session.add(current_battle_info)
            session.flush()
            return_dict["Table_ID"] = current_battle_info.id
            return_dict["Exists"] = False
            return return_dict
        else:
            return_dict["Table_ID"] = exists.id
            return_dict["Exists"] = True
            return return_dict
