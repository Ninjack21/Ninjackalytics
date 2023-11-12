from ninjackalytics.database.models import pokemonmetadata
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
from ninjackalytics.database.database import SessionLocal
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
from contextlib import contextmanager
import sqlalchemy


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def contains_mon(row, mon):
    return row.str.contains(mon).any()


def recalc_metadata_table_info():
    ta = TableAccessor()
    battle_info = ta.get_battle_info()
    recent_battle_info = battle_info[
        battle_info["Date_Submitted"] > (datetime.now() - timedelta(days=14))
    ]
    teams = ta.get_teams()
    formats = [f for f in battle_info["Format"].unique() if f != "gen9ou"]

    for f in formats:
        previous_data = ta.get_pokemonmetadata()
        previously_seen_mons = previous_data["Pokemon"][previous_data["Format"] == f]
        with session_scope() as session:
            print(f"=================Starting format {f}===================")
            f_info = recent_battle_info[recent_battle_info["Format"] == f]
            total_battles = len(f_info)
            team_ids = pd.concat([f_info["P1_team"], f_info["P2_team"]]).unique()
            # now get all of the pokemon in each team
            format_teams = teams[teams["id"].isin(team_ids)]
            all_mons = pd.concat(
                [format_teams[f"Pok{i}"] for i in range(1, 7)]
            ).unique()
            all_mons = [mon for mon in all_mons if mon != None]
            # check if any of the previously_seen_pokemon no longer show up
            for mon in previously_seen_mons:
                if mon not in all_mons:
                    # if so, update the popularity to 0
                    existing_data = (
                        session.query(pokemonmetadata)
                        .filter_by(Format=f, Pokemon=mon)
                        .first()
                    )
                    existing_data.Popularity = 0
            for mon in tqdm(all_mons):
                # the repr of a team is a list of the mon names so we can use that to get which teams contain each mon
                mon_teams_idx = teams.apply(lambda row: contains_mon(row, mon), axis=1)
                mon_teams = teams[mon_teams_idx]
                # now I can get the winrate of each team
                pokemon_meta_data_kwargs = {
                    "Format": f,
                    "Pokemon": mon,
                }
                mon_wins = 0
                mon_battles = 0
                for team_id in mon_teams["id"]:
                    p1_team_info = f_info[f_info["P1_team"] == team_id]
                    p2_team_info = f_info[f_info["P2_team"] == team_id]
                    all_battles = len(p1_team_info) + len(p2_team_info)
                    mon_battles += all_battles

                    p1_wins = len(
                        p1_team_info[p1_team_info["Winner"] == p1_team_info["P1"]]
                    )
                    p2_wins = len(
                        p2_team_info[p2_team_info["Winner"] == p2_team_info["P2"]]
                    )
                    mon_wins += p1_wins + p2_wins

                winrate = mon_wins / mon_battles * 100
                pokemon_meta_data_kwargs["Winrate"] = winrate
                pokemon_meta_data_kwargs["SampleSize"] = mon_battles
                pokemon_meta_data_kwargs["Popularity"] = (
                    mon_battles / total_battles * 100
                )

                existing_data = (
                    session.query(pokemonmetadata)
                    .filter_by(Format=f, Pokemon=mon)
                    .first()
                )
                if existing_data is None:  # if combo new, add it
                    new_data = pokemonmetadata(**pokemon_meta_data_kwargs)
                    session.add(new_data)
                    session.commit()  # ensure in db for if shows up again

                else:  # otherwise, update it
                    existing_data.Winrate = winrate
                    existing_data.SampleSize = mon_battles
                    session.commit()
                # commit the data to the database upon completion of the formats mons
                session.commit()
