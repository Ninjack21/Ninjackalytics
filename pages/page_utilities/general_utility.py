import os
import difflib
import random
from ninjackalytics.services.database_interactors.table_accessor import (
    TableAccessor,
    session_scope,
)
from ninjackalytics.database.models import battle_info
from sqlalchemy import func
import pandas as pd
from typing import List, Tuple


def _get_sprites():
    current_dir = os.path.dirname(__file__)
    while current_dir != "/":
        if os.path.basename(current_dir) == "Ninjackalytics":
            break
        current_dir = os.path.dirname(current_dir)

    sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
    sprites = os.listdir(sprite_dir)
    gifs = [sprite.split(".gif")[0] for sprite in sprites if sprite.endswith(".gif")]
    pngs = [sprite.split(".png")[0] for sprite in sprites if sprite.endswith(".png")]
    return sprite_dir, gifs, pngs


def _return_sprite_path(sprite_dir, sprite):
    return os.path.join(sprite_dir, sprite).split("Ninjackalytics")[-1]


def find_closest_sprite(name):
    sprite_dir, gifs, pngs = _get_sprites()
    name = name.lower()

    # First, look for an exact match in gifs
    if name in gifs:
        name = name + ".gif"
        return _return_sprite_path(sprite_dir, name)

    # now look for an exact match in pngs
    if name in pngs:
        name = name + ".png"
        return _return_sprite_path(sprite_dir, name)

    # Otherwise, find the closest match or subset in gifs
    closest_match = difflib.get_close_matches(name, gifs, n=1)
    if closest_match:
        closest_match = closest_match[0] + ".gif"
        return _return_sprite_path(sprite_dir, closest_match)
    else:
        for sprite in gifs:
            if name.lower() in sprite.lower():
                sprite = sprite + ".gif"
                return _return_sprite_path(sprite_dir, sprite)

    # Otherwise, find the closest match or subset in pngs
    closest_match = difflib.get_close_matches(name, pngs, n=1)
    if closest_match:
        closest_match = closest_match[0] + ".png"
        return _return_sprite_path(sprite_dir, closest_match)
    else:
        for sprite in pngs:
            if name.lower() in sprite.lower():
                sprite = sprite + ".png"
                return _return_sprite_path(sprite_dir, sprite)

    return None


def get_random_sprite():
    sprite_dir, gifs, pngs = _get_sprites()
    return _return_sprite_path(sprite_dir, random.choice(gifs) + ".gif")


class DatabaseData:
    def __init__(self, format=None):
        self.ta = TableAccessor()
        # --- first determine the viable formats before querying data ---
        self.viable_formats = self.get_viable_formats()

        # only load 1 format's data. if not specified, just pick one of viable formats for init loading
        if format:
            f_conditions = {
                "Format": {"op": "==", "value": format},
            }
            # --- now use viable formats to limit queries ---
            self.pvpmetadata = self.ta.get_pvpmetadata(conditions=f_conditions)
            self.pokemonmetadata = self.ta.get_pokemonmetadata(conditions=f_conditions)
        else:
            self.pvpmetadata = None
            self.pokemonmetadata = None

    def get_pvpmetadata(self):
        return self.pvpmetadata

    def get_pokemonmetadata(self):
        return self.pokemonmetadata

    # NOTE this is used to determine default format on main page as well as what formats are viable
    # 4k is min for metadata tables
    def get_viable_formats(self, min_battles=4000):
        sessionmaker = self.ta.session_maker
        with session_scope(sessionmaker()) as session:
            viable_formats = (
                session.query(battle_info.Format)
                .group_by(battle_info.Format)
                .having(func.count(battle_info.Format) >= min_battles)
                .all()
            )
            viable_formats = [f[0] for f in viable_formats]

        return viable_formats


class FormatData:
    def __init__(self, battle_format: str, db: DatabaseData):
        # TODO: FormatData no longer needed due to TA updates but leaving for legacy content
        # TODO: Should remove this class and go refactor code dependent on it to instead utilize
        # the DatabaseData class directly with a provided format
        self.battle_format = battle_format
        self.db = db

        self.format_pvpmetadata = self.db.get_pvpmetadata()
        self.format_metadata = self.db.get_pokemonmetadata()

        self.top30 = self.format_metadata.sort_values(
            by="Popularity", ascending=False
        ).head(30)

    def get_format_available_mons(self):
        mons = self.format_metadata["Pokemon"][self.format_metadata["SampleSize"] >= 30]
        return mons.tolist()


class WinrateCalculator:
    def __init__(self, format_data: FormatData, engine_name: str = "antimeta"):
        self.format_data = format_data
        self.engine_name = engine_name
        winrate_engine = {
            "synergy": self._synergy_winrate,
            "antimeta": self._antimeta_winrate,
            "star_mon": self._star_mon_winrate,
        }
        self.engine = winrate_engine[self.engine_name]

    def normalized_winrate(
        self, team_winrates: pd.DataFrame, opposing_team=None
    ) -> pd.DataFrame:
        # if opposing_team is None, we are calculating the winrate against the meta
        if opposing_team is None:
            top30 = self.format_data.top30.copy()
            top30 = top30.set_index("Pokemon")
            top30 = top30.rename(columns={"Winrate": "Top30 Base Winrate"})
            team_winrates = team_winrates.rename(columns={"winrate": "Team Winrate"})
            merged_df = team_winrates.merge(top30, how="left", on="Pokemon")
            merged_df["Relative Popularity"] = (
                merged_df["Popularity"] / merged_df["Popularity"].sum()
            )
        # if opposing_team is not None, we are calculating the winrate against another team
        else:
            other_mons = self.format_data.format_metadata.copy()
            other_mons = other_mons[other_mons["Pokemon"].isin(opposing_team)]
            other_mons = other_mons.set_index("Pokemon")
            other_mons = other_mons.rename(
                columns={"Winrate": "Opposing Team Base Winrate"}
            )
            team_winrates = team_winrates.rename(columns={"winrate": "Team Winrate"})
            merged_df = team_winrates.merge(other_mons, how="left", on="Pokemon")
            merged_df["Relative Popularity"] = (
                merged_df["Popularity"] / merged_df["Popularity"].sum()
            )

        merged_df["Normalized Winrate"] = (
            merged_df["Team Winrate"] * merged_df["Relative Popularity"]
        )
        merged_df = merged_df.drop(columns=["Popularity", "Relative Popularity"])

        return merged_df["Normalized Winrate"].sum()

    def get_team_winrate_against_meta(self, team: List[str]):
        engine_method = self.engine
        winrates = engine_method(team)
        return winrates

    def get_team_winrate_against_other_team(self, team1: List[str], team2: List[str]):
        team1vteam2 = self.engine(team1, team2)

        return

    def _synergy_winrate(self, team: List[str]):
        pass

    def _star_mon_winrate(self, team: List[str]):
        pass

    def _antimeta_winrate(self, team1: List[str], team2: List[str] = None):
        winrates = {}
        # if team2 is None, we are calculating the winrate against the meta
        if team2 is None:
            for top30mon in self.format_data.top30["Pokemon"].tolist():
                (
                    team_mons_in_pokemon1,
                    team_mons_in_pokemon2,
                ) = self._get_mon_vs_mon_winrates(top30mon, team1)
                team_v_top30mon_df = self._merge_team_mons_into_mon1(
                    team_mons_in_pokemon1, team_mons_in_pokemon2
                )
                # if the cumulative team1 sample size into a mon is less than 70, use presumed
                if team_v_top30mon_df["SampleSize"].sum() < 70:
                    winrates[top30mon] = self._get_presumed_winrate(top30mon)
                else:
                    # handle antimeta winrate calc
                    winrate = team_v_top30mon_df[
                        "Winrate"
                    ].mean()  # assume each mon's weight is equal
                    winrates[top30mon] = winrate
        else:
            # if team2 is not None, we are calculating the winrate against another team
            for opposing_mon in team2:
                (
                    team_mons_in_pokemon1,
                    team_mons_in_pokemon2,
                ) = self._get_mon_vs_mon_winrates(opposing_mon, team1)
                team1_v_team2_df = self._merge_team_mons_into_mon1(
                    team_mons_in_pokemon1, team_mons_in_pokemon2
                )
                # if the cumulative team1 sample size into a mon is less than 20, use presumed
                if team1_v_team2_df["SampleSize"].sum() < 20:
                    winrates[opposing_mon] = self._get_presumed_winrate(opposing_mon)
                else:
                    # handle antimeta winrate calc
                    winrate = team1_v_team2_df["Winrate"].mean()
                    winrates[opposing_mon] = winrate

        winrates = pd.DataFrame.from_dict(winrates, orient="index", columns=["winrate"])
        winrates.index.name = "Pokemon"
        return winrates

    def _get_mon_vs_mon_winrates(
        self, opposing_mon: str, team: List[str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        format_pvp = self.format_data.format_pvpmetadata
        team_mons_in_pokemon1 = format_pvp[
            (format_pvp["Pokemon1"].isin(team))
            & (format_pvp["Pokemon2"] == opposing_mon)
        ].copy()
        team_mons_in_pokemon2 = format_pvp[
            (format_pvp["Pokemon2"].isin(team))
            & (format_pvp["Pokemon1"] == opposing_mon)
        ].copy()

        # Check if the opposing mon exists in the team
        if opposing_mon in team:
            # Remove the opposing mon instance from team_mons_in_pokemon2 dataframe
            team_mons_in_pokemon2 = team_mons_in_pokemon2[
                team_mons_in_pokemon2["Pokemon2"] != opposing_mon
            ]

        return team_mons_in_pokemon1, team_mons_in_pokemon2

    def _merge_team_mons_into_mon1(
        self, team_mons_in_mon1: pd.DataFrame, team_mons_in_mon2: pd.DataFrame
    ) -> pd.DataFrame:
        team_mons_in_mon2["Winrate"] = 100 - team_mons_in_mon2["Winrate"]
        team_mons_in_mon2 = team_mons_in_mon2.rename(
            columns={"Pokemon1": "Pokemon2", "Pokemon2": "Pokemon1"}
        )
        team_mons_in_mon1 = pd.concat(
            [team_mons_in_mon1, team_mons_in_mon2], ignore_index=True
        )
        return team_mons_in_mon1

    def _get_presumed_winrate(self, mon: str) -> float:
        format_metadata = self.format_data.format_metadata
        return (
            100
            - format_metadata[format_metadata["Pokemon"] == mon]["Winrate"].values[0]
        )
