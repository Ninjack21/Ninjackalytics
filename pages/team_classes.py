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
        self.format_info = self.db.get_battle_info()[
            self.db.get_battle_info()["Format"] == self.battle_format
        ]
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


class WinrateCalculator:
    winrate_engine = {
        "synergy": self._synergy_winrate,
        "antimeta": self._antimeta_winrate,
        "star_mon": self._star_mon_winrate,
    }

    def __init__(self, format_data: FormatData, engine_name: str):
        self.format_data = format_data
        self.engine_name = engine_name

    def get_team_winrate_against_meta(self, team: List[str]):
        engine_method = self.winrate_engine[self.engine_name]
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
        team_mon_in_pokemon1 = format_pvp[
            (format_pvp["Pokemon1"].isin(team)) & (format_pvp["Pokemon2"] == top30mon)
        ].copy()
        team_mon_in_pokemon2 = format_pvp[
            (format_pvp["Pokemon2"].isin(team)) & (format_pvp["Pokemon1"] == top30mon)
        ].copy()
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
        format_metadata = self.format_data.format_metadata
        # reverse the winrate because we want to get the team's expected winrate into the top30 mon
        return (
            100
            - format_metadata[format_metadata["Pokemon"] == top30mon : str][
                "Winrate"
            ].values[0]
        )


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
        engine_name: str = "synergy",
    ):
        # handle the case where the current team is empty
        if len(current_team) == 0:
            current_team = [self._pick_random_top30_mon()]

        remaining_slots = 6 - len(current_team)
        while remaining_slots > 0:
            pass

    def _pick_random_top30_mon(self):
        mon = self.format_data.top30.sample(n=1)["Pokemon"].values[0]
        return mon

    def _get_team_winrates_against_top_30(
        self,
        current_team: List[str],
    ):
        # TODO: break this down into smaller functions.
        # TODO: should winrate calcs be own class to allow for different methods of calculating winrates?

        winrates = {}
        format_pvp = self.format_data.format_pvpmetadata
        for mon in self.format_data.top30["Pokemon"].tolist():
            team_mon_in_pokemon1 = format_pvp[
                (format_pvp["Pokemon1"].isin(current_team))
                & (format_pvp["Pokemon2"] == mon)
            ].copy()
            team_mon_in_pokemon2 = format_pvp[
                (format_pvp["Pokemon2"].isin(current_team))
                & (format_pvp["Pokemon1"] == mon)
            ].copy()

            total_samplesize = (
                team_mon_in_pokemon1["SampleSize"].sum()
                + team_mon_in_pokemon2["SampleSize"].sum()
            )
            if total_samplesize < 30:
                # if very low data, then presume winrate against mon is opposite of mon general WR
                format_metadata = self.format_data.format_metadata
                winrates[mon] = (
                    100
                    - format_metadata[format_metadata["Pokemon"] == mon][
                        "Winrate"
                    ].values[0]
                )
                continue
            else:
                # if in mon1 then we have the winrate against the top30 mon, which we want
                team_mon_in_pokemon1["Weighted Winrate"] = (
                    team_mon_in_pokemon1["Winrate"]
                    * team_mon_in_pokemon1["SampleSize"]
                    / team_mon_in_pokemon1["SampleSize"].sum()
                )

                winrate_in_mon1 = team_mon_in_pokemon1["Weighted Winrate"].sum()
                in_mon1_samplesize = team_mon_in_pokemon1["SampleSize"].sum()

                # if in mon2 then we have the winrate of top30 against us, so we need 1-winrate, but gets goofy with
                # weighted winrates
                # this is inefficient and it could be done in one line but won't slow it down to an amount the user will
                # care about but it WILL make it much more intuitive how it works for future maintenance
                team_mon_in_pokemon2["Reversed Winrate"] = (
                    100 - team_mon_in_pokemon2["Winrate"]
                )
                # use reversed winrates to get the winrate of team mons against top30 mons like desired
                team_mon_in_pokemon2["Weighted Winrate"] = (
                    team_mon_in_pokemon2["Reversed Winrate"]
                    * team_mon_in_pokemon2["SampleSize"]
                    / team_mon_in_pokemon2["SampleSize"].sum()
                )

                winrate_in_mon2 = team_mon_in_pokemon2["Weighted Winrate"].sum()
                in_mon2_samplesize = team_mon_in_pokemon2["SampleSize"].sum()

                # now we can calculate the overall winrate
                winrate = (winrate_in_mon1 * in_mon1_samplesize / total_samplesize) + (
                    winrate_in_mon2 * in_mon2_samplesize / total_samplesize
                )

                winrates[mon] = winrate

        winrates = pd.DataFrame.from_dict(winrates, orient="index", columns=["winrate"])
        return winrates


# TODO: build DisplayTeam class
class DisplayTeam:
    pass
