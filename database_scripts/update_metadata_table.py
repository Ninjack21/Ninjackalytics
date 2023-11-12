import pandas as pd
from ninjackalytics.database.models import metadata
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
from tqdm import tqdm
from datetime import datetime, timedelta


def update_metadata_table():
    ta = TableAccessor()
    battle_info = ta.get_battle_info()
    recent_battle_info = battle_info[
        battle_info["Date"] > datetime.now() - timedelta(days=14)
    ]
    teams = ta.get_teams()

    for f in tqdm(battle_info["Format"].unique()):
        f_info = recent_battle_info[recent_battle_info["Format"] == f]
        team_ids = pd.concat([f_info["P1_team"], f_info["P2_team"]]).unique()
        # now get all of the pokemon in each team
        format_teams = teams[teams["id"].isin(team_ids)]
        all_mons = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
        for mon in all_mons:
            # the repr of a team is a list of the mon names so we can use that to get which teams contain each mon
            mon_teams = format_teams[format_teams["__repr__()"].str.contains(mon)]
            # now I can get the winrate of each team
            winrates = []
            for team_id in mon_teams["id"]:
                p1_team_info = f_info[f_info["P1_team"] == team_id]
                p2_team_info = f_info[f_info["P2_team"] == team_id]
                # now check within each df for where the winner was the name in "P1" or "P2" columns (for the teams
                # respectively)
                # then get the winrate and average them, weighting by the number of battles
                p1_wins = p1_team_info[p1_team_info["Winner"] == p1_team_info["P1"]]
                p2_wins = p2_team_info[p2_team_info["Winner"] == p2_team_info["P2"]]
