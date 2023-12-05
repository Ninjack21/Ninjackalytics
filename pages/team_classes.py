from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta

# TODO: keep in mind team preview as well
# TODO: build unit tests for appropriate classes to verify working as expected and to look for edge cases


class DatabaseData:
    def __init__(self):
        self.ta = TableAccessor()
        self.battle_info = self.ta.get_battle_info()
        self.teams = self.ta.get_teams()
        self.pvpmetadata = self.ta.get_pvpmetadata()
        self.pokemonmetadata = self.ta.get_pokemonmetadata()

    def get_battle_info(self):
        return self.battle_info

    def get_teams(self):
        return self.teams

    def get_pvpmetadata(self):
        return self.pvpmetadata

    def get_pokemonmetadata(self):
        return self.pokemonmetadata


class FormatData:
    def __init__(self, battle_format: str, db: DatabaseData):
        self.battle_format = battle_format
        self.db = db
        db_info = self.db.get_battle_info()
        self.format_info = db_info[db_info["Format"] == self.battle_format]
        self.format_teams = self.db.get_teams()[
            self.db.get_teams()["id"].isin(
                self.format_info["P1_team"].tolist()
                + self.format_info["P2_team"].tolist()
            )
        ]
        self.format_pvpmetadata = self.db.get_pvpmetadata()[
            self.db.get_pvpmetadata()["Format"] == self.battle_format
        ]
        self.format_metadata = self.db.get_pokemonmetadata()[
            self.db.get_pokemonmetadata()["Format"] == self.battle_format
        ]
        self.top30 = self.format_metadata.sort_values(
            by="Popularity", ascending=False
        ).head(30)

    def get_format_available_mons(self):
        mons = self.format_metadata["Pokemon"][self.format_metadata["SampleSize"] >= 30]
        return mons.tolist()


class WinrateCalculator:
    def __init__(self, format_data: FormatData, engine_name: str):
        self.format_data = format_data
        self.engine_name = engine_name
        winrate_engine = {
            "synergy": self._synergy_winrate,
            "antimeta": self._antimeta_winrate,
            "star_mon": self._star_mon_winrate,
        }
        self.engine = winrate_engine[self.engine_name]

    def normalized_winrate(self, team_winrates: pd.DataFrame) -> pd.DataFrame:
        top30 = self.format_data.top30.copy()
        top30 = top30.set_index("Pokemon")
        top30 = top30.rename(columns={"Winrate": "Top30 Base Winrate"})
        team_winrates = team_winrates.rename(columns={"winrate": "Team Winrate"})
        merged_df = team_winrates.merge(top30, how="left", on="Pokemon")
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

    def _synergy_winrate(self, team: List[str]):
        pass

    def _star_mon_winrate(self, team: List[str]):
        pass

    def _antimeta_winrate(self, team: List[str]):
        winrates = {}
        for top30mon in self.format_data.top30["Pokemon"].tolist():
            (
                team_mons_in_pokemon1,
                team_mons_in_pokemon2,
            ) = self._get_mon_vs_mon_winrates(top30mon, team)
            team_v_top30mon_df = self._merge_team_mons_into_mon1(
                team_mons_in_pokemon1, team_mons_in_pokemon2
            )
            if team_v_top30mon_df["SampleSize"].sum() < 30:
                winrates[top30mon] = self._get_presumed_winrate(top30mon)
            else:
                # handle antimeta winrate calc
                winrate = team_v_top30mon_df[
                    "Winrate"
                ].mean()  # assume each mon's weight is equal
                winrates[top30mon] = winrate
        return pd.DataFrame.from_dict(winrates, orient="index", columns=["winrate"])

    def _get_mon_vs_mon_winrates(
        self, top30mon: str, team: List[str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        format_pvp = self.format_data.format_pvpmetadata
        team_mons_in_pokemon1 = format_pvp[
            (format_pvp["Pokemon1"].isin(team)) & (format_pvp["Pokemon2"] == top30mon)
        ].copy()
        team_mons_in_pokemon2 = format_pvp[
            (format_pvp["Pokemon2"].isin(team)) & (format_pvp["Pokemon1"] == top30mon)
        ].copy()

        # if a top30 mon is on your team and in the top30 then it will check itself against itself.
        # to prevent it showing up in both team1 and team2 then if the team contains any mons in the top30
        # then we will remove the top30mon from the team_mons_in_pokemon2 dataframe
        if (
            len(set(team).intersection(set(self.format_data.top30["Pokemon"].tolist())))
            > 0
        ):
            team_mons_in_pokemon2 = team_mons_in_pokemon2[
                team_mons_in_pokemon2["Pokemon2"] != top30mon
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

    def _get_presumed_winrate(self, top30mon: str) -> float:
        top30 = self.format_data.top30
        # reverse the winrate because we want to get the team's expected winrate into the top30 mon
        return 100 - top30[top30["Pokemon"] == top30mon]["Winrate"].values[0]


# TODO: complete design utilizing WinrateCalculator
class TeamSolver:
    def __init__(self, db: DatabaseData, battle_format: str):
        self.db = db
        self.format_data = FormatData(battle_format=battle_format, db=self.db)

    def solve_for_remainder_of_team(
        self,
        current_team: List[str],
        creativity: int,
        ignore_mons: List[str] = [],
        engine_name: str = "antimeta",
    ):
        winrate_calculator = WinrateCalculator(
            format_data=self.format_data, engine_name=engine_name
        )
        # handle the case where the current team is empty
        if len(current_team) == 0:
            current_team = [self._pick_random_top30_mon()]

        remaining_slots = 6 - len(current_team)
        while remaining_slots > 0:
            current_winrates = winrate_calculator.get_team_winrate_against_meta(
                current_team
            )
            normalized_winrate = winrate_calculator.normalized_winrate(current_winrates)

    def _pick_random_top30_mon(self):
        mon = self.format_data.top30.sample(n=1)["Pokemon"].values[0]
        return mon


# TODO: build DisplayTeam class
class DisplayTeam:
    pass
