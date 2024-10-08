import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)
from ninjackalytics.database.models import (
    pokemonmetadata,
    pvpmetadata,
    battle_info,
)
from ninjackalytics.services.database_interactors.table_accessor import (
    TableAccessor,
    session_scope,
)
from ninjackalytics.database.database import get_sessionlocal
import pandas as pd
from tqdm import tqdm
from contextlib import contextmanager
import sqlalchemy
from itertools import combinations
from math import comb
from sqlalchemy import func


# ----------------- db interactions -----------------
@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_sessionlocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_active_teams(bi_df, ta):
    p1_teams = bi_df["P1_team"].unique()
    p2_teams = bi_df["P2_team"].unique()
    all_team_ids = list(set(list(p1_teams) + list(p2_teams)))
    teams = ta.get_teams()
    teams = teams[teams["id"].isin(all_team_ids)]
    return teams


def update_no_longer_seen_mons(all_mons, previously_seen_mons, fmat):
    no_longer_seen_mons = [mon for mon in previously_seen_mons if mon not in all_mons]
    with session_scope() as session:
        for mon in no_longer_seen_mons:
            # Delete the row from pokemonmetadata table
            session.query(pokemonmetadata).filter_by(Format=fmat, Pokemon=mon).delete()

            # Delete all rows in pvpmetadata table for that particular mon + format combo
            session.query(pvpmetadata).filter_by(Format=fmat).filter(
                sqlalchemy.or_(pvpmetadata.Pokemon1 == mon, pvpmetadata.Pokemon2 == mon)
            ).delete()


def upload_new_data(session, db_class, row: dict):
    if "Pokemon2" not in row:
        existing_data = (
            session.query(db_class)
            .filter_by(Format=row["Format"], Pokemon=row["Pokemon"])
            .first()
        )
        if existing_data is None:
            new_data = db_class(**row)
            session.add(new_data)
        else:
            existing_data.Winrate = row["Winrate"]
            existing_data.SampleSize = row["SampleSize"]
            existing_data.Popularity = row["Popularity"]
    else:
        insert_or_update_matchup(session, row)


# built separate func to handle alphabetizing mon1 into mon2
def insert_or_update_matchup(session, row: dict):
    mon1, mon2 = row["Pokemon1"], row["Pokemon2"]
    fmat = row["Format"]
    if mon1 > mon2:
        # ensure alphabetical standard
        mon1, mon2 = mon2, mon1
        # now have to reverse winrate
        winrate = round(100 - row["Winrate"], 2)
        row["Winrate"] = winrate
        # remember, reversed the order of the mons
        row["Pokemon1"] = mon1
        row["Pokemon2"] = mon2

    existing_matchup = (
        session.query(pvpmetadata)
        .filter_by(Pokemon1=mon1, Pokemon2=mon2, Format=fmat)
        .first()
    )
    if existing_matchup is None:
        new_matchup = pvpmetadata(**row)
        session.add(new_matchup)
    else:
        existing_matchup.Winrate = row["Winrate"]
        existing_matchup.SampleSize = row["SampleSize"]


# ----------------- helper functions -----------------
def contains_mon(row, mon):
    return row.str.contains(mon).any()


def get_rank_limit_based_on_quantile(battle_info: pd.DataFrame, quantile: float):
    rank_limit = battle_info["Rank"].quantile(quantile, interpolation="nearest")
    return round(rank_limit)


# ----------------- main function -----------------
def update_metadata():
    threshold = 0.8
    ta = TableAccessor()
    bi_df, teams = get_battle_info_and_teams_for_viable_formats(threshold, ta)
    for fmat in bi_df["Format"].unique():
        mon_teams_dict, fmat_df = (
            get_fmat_mon_teams_dict_and_remove_no_longer_found_mons(
                fmat, bi_df, teams, ta, threshold
            )
        )
        new_pokemon_metadata = calculate_overall_metadata_values(
            fmat_df, mon_teams_dict
        )
        new_pvp_metadata = calculate_mon_v_mon_metadata_values(fmat_df, mon_teams_dict)
        upload_new_metadata(new_pokemon_metadata, new_pvp_metadata)


def get_battle_info_and_teams_for_viable_formats(metadata_quantile_threshold, ta):
    with session_scope() as session:
        # require that at a minimum, ~800 high rank battles be found before storing data
        viable_formats = (
            session.query(battle_info.Format)
            .group_by(battle_info.Format)
            .having(
                func.count(battle_info.Format)
                >= (800 / (1 - metadata_quantile_threshold))
            )
            .all()
        )
        viable_formats = [f[0] for f in viable_formats]

        conditions = {
            "Format": {"op": "in", "value": viable_formats},
        }

        bi_df = ta.get_battle_info(conditions=conditions)
        teams = get_active_teams(bi_df, ta)
        return bi_df, teams


def get_fmat_mon_teams_dict_and_remove_no_longer_found_mons(
    fmat, bi_df, all_teams, ta, quantile_threshold
):
    f_condition = {
        "Format": {"op": "==", "value": fmat},
    }
    print(f"=================Starting format {fmat}===================")
    f_info = bi_df[bi_df["Format"] == fmat]
    # get up to the last 2200 / (1-threshold) most recent battles (quantile thresholds not perfect so
    # 2200 helps ensure will get at least 2k, if that many exist, each time)
    f_info = f_info.sort_values(by="Date_Submitted", ascending=False)
    f_info = f_info.head(round(2200 / (1 - quantile_threshold)))
    rank_limit = get_rank_limit_based_on_quantile(f_info, quantile_threshold)
    f_info = f_info[f_info["Rank"] >= rank_limit]
    print(f"Rank Limit: {rank_limit} | Battles: {len(f_info)}")
    team_ids = pd.concat([f_info["P1_team"], f_info["P2_team"]]).unique()
    # now get all of the pokemon in each team
    format_teams = all_teams[all_teams["id"].isin(team_ids)]
    all_mons = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    # 12-6-23: got bad teams with a mon with "|" in it so ensure this does not populate the db
    all_mons = [mon for mon in all_mons if mon != None and "|" not in mon]
    current_pokemon_metadata = ta.get_pokemonmetadata(f_condition)
    update_no_longer_seen_mons(
        all_mons, current_pokemon_metadata["Pokemon"].unique(), fmat
    )
    mon_teams_dict = {
        mon: format_teams[
            format_teams.apply(lambda row: contains_mon(row, mon), axis=1)
        ]
        for mon in all_mons
    }
    return mon_teams_dict, f_info


def calculate_overall_metadata_values(fmat_df, mon_teams_dict):
    new_pokemon_metadata = []
    total_battles = len(fmat_df)
    for mon in tqdm(mon_teams_dict.keys(), desc="Calculating Overall Pokemon Metadata"):
        mon_teams = mon_teams_dict[mon]
        # now I can get the winrate of each team
        pokemon_meta_data_kwargs = {
            "Format": fmat_df["Format"].iloc[0],
            "Pokemon": mon,
        }
        mon_wins = 0
        mon_battles = 0
        for team_id in mon_teams["id"]:
            p1_team_info = fmat_df[fmat_df["P1_team"] == team_id]
            p2_team_info = fmat_df[fmat_df["P2_team"] == team_id]
            all_battles = len(p1_team_info) + len(p2_team_info)
            mon_battles += all_battles

            p1_wins = len(p1_team_info[p1_team_info["Winner"] == p1_team_info["P1"]])
            p2_wins = len(p2_team_info[p2_team_info["Winner"] == p2_team_info["P2"]])
            mon_wins += p1_wins + p2_wins

        winrate = round(mon_wins / mon_battles * 100, 2)
        pokemon_meta_data_kwargs["Winrate"] = winrate
        pokemon_meta_data_kwargs["SampleSize"] = mon_battles
        pokemon_meta_data_kwargs["Popularity"] = mon_battles / total_battles * 100
        new_pokemon_metadata.append(pokemon_meta_data_kwargs)
    return new_pokemon_metadata


def calculate_mon_v_mon_metadata_values(fmat_df, mon_teams_dict):
    new_pvp_metadata = []
    total_combinations = comb(len(fmat_df.keys()), 2)
    for mon1, mon2 in tqdm(
        combinations(mon_teams_dict.keys(), 2),
        total=total_combinations,
        desc="Calculating All PvP Winrates",
    ):
        mon1_teams = mon_teams_dict[mon1]
        mon2_teams = mon_teams_dict[mon2]
        # now I can get the winrate of each team
        pvp_meta_data_kwargs = {
            "Format": fmat_df["Format"].iloc[0],
            "Pokemon1": mon1,
            "Pokemon2": mon2,
        }
        # Get all battles involving mon1 teams
        mon1_p1_battles = fmat_df[
            fmat_df["P1_team"].isin(mon1_teams["id"])
            & fmat_df["P2_team"].isin(mon2_teams["id"])
        ]
        mon1_p2_battles = fmat_df[
            fmat_df["P2_team"].isin(mon1_teams["id"])
            & fmat_df["P1_team"].isin(mon2_teams["id"])
        ]

        # Compute the total number of battles
        all_battles = len(mon1_p1_battles) + len(mon1_p2_battles)
        pvp_meta_data_kwargs["SampleSize"] = all_battles

        if all_battles > 0:
            # Compute the total number of wins
            p1_wins = len(
                mon1_p1_battles[mon1_p1_battles["Winner"] == mon1_p1_battles["P1"]]
            )
            p2_wins = len(
                mon1_p2_battles[mon1_p2_battles["Winner"] == mon1_p2_battles["P2"]]
            )
            total_wins = p1_wins + p2_wins

            # Compute the winrate
            winrate = round(total_wins / all_battles * 100, 2)
            pvp_meta_data_kwargs["Winrate"] = round(winrate, 2)

        else:
            # if no data, just leave winrate at 0
            winrate = 0
            pvp_meta_data_kwargs["Winrate"] = 0

        new_pvp_metadata.append(pvp_meta_data_kwargs)

    return new_pvp_metadata


def upload_new_metadata(new_pokemon_metadata, new_pvp_metadata):
    with session_scope() as session:
        # now upload all the new data for the current format
        for row in tqdm(new_pokemon_metadata, desc="Uploading Pokemon Metadata"):
            upload_new_data(session, pokemonmetadata, row)
        print("Finished staging Pokemon Metadata")

        for row in tqdm(new_pvp_metadata, desc="Uploading PvP Metadata"):
            upload_new_data(session, pvpmetadata, row)
        print("Finished staging PvP Metadata")

    print("Data committed to database")


if __name__ == "__main__":
    update_metadata()
