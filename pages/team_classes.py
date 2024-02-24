from ninjackalytics.services.database_interactors.table_accessor import (
    TableAccessor,
    session_scope,
)
from ninjackalytics.database.models import battle_info
import pandas as pd
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from sqlalchemy import func


class DatabaseData:
    def __init__(self):
        self.ta = TableAccessor()
        # --- first determine the viable formats before querying data ---
        self.viable_formats = self.get_viable_formats()

        f_conditions = {
            "Format": {"op": "in", "value": self.viable_formats},
        }

        # --- now use viable formats to limit queries ---
        self.pvpmetadata = self.ta.get_pvpmetadata(conditions=f_conditions)
        self.pokemonmetadata = self.ta.get_pokemonmetadata(conditions=f_conditions)

    def get_pvpmetadata(self):
        return self.pvpmetadata

    def get_pokemonmetadata(self):
        return self.pokemonmetadata

    # NOTE this is used to determine default format on main page as well as what formats are viable
    def get_viable_formats(self):
        sessionmaker = self.ta.session_maker
        with session_scope(sessionmaker()) as session:
            viable_formats = (
                session.query(battle_info.Format)
                .group_by(battle_info.Format)
                .having(
                    func.count(battle_info.Format) >= 4000
                )  # 4k is min for metadata tables
                .all()
            )
            viable_formats = [f[0] for f in viable_formats]

        return viable_formats


class FormatData:
    def __init__(self, battle_format: str, db: DatabaseData):
        self.battle_format = battle_format
        self.db = db

        format_conditions = {"Format": {"op": "==", "value": self.battle_format}}

        self.format_pvpmetadata = self.db.get_pvpmetadata(conditions=format_conditions)
        self.format_metadata = self.db.get_pokemonmetadata(conditions=format_conditions)

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
        return winrates

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
            # if the cumulative team sample size into a mon is less than 70, use presumed
            if team_v_top30mon_df["SampleSize"].sum() < 70:
                winrates[top30mon] = self._get_presumed_winrate(top30mon)
            else:
                # handle antimeta winrate calc
                winrate = team_v_top30mon_df[
                    "Winrate"
                ].mean()  # assume each mon's weight is equal
                winrates[top30mon] = winrate
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

    def _get_presumed_winrate(self, top30mon: str) -> float:
        top30 = self.format_data.top30
        # reverse the winrate because we want to get the team's expected winrate into the top30 mon
        return 100 - top30[top30["Pokemon"] == top30mon]["Winrate"].values[0]


class CreativityRestrictor:
    def __init__(self, creativity: int, format_data: FormatData):
        self.creativity = creativity
        self.format_data = format_data

    def restrict_available_mons(
        self, available_mons: List[str], current_team: List[str]
    ) -> Tuple[float, float]:
        metadata = self.format_data.format_metadata
        if self.creativity == 0:
            # remove current team from available_mons and return
            available_mons = [mon for mon in available_mons if mon not in current_team]
            return available_mons
        else:
            # ---- calculate general data once -----
            target_popularity = self._get_target_avg_popularity()
            current_avg_popularity = metadata[metadata["Pokemon"].isin(current_team)][
                "Popularity"
            ].mean()
            remaining_slots = 6 - len(current_team)
            (
                min_popularity,
                max_popularity,
            ) = self._define_popularity_bounds_for_available_pokemon(
                current_avg_popularity, target_popularity, remaining_slots
            )
            available_mons = metadata[
                (metadata["Pokemon"].isin(available_mons))
                & (metadata["Pokemon"].isin(current_team) == False)
                & (metadata["Popularity"] >= min_popularity)
                & (metadata["Popularity"] <= max_popularity)
            ]["Pokemon"].tolist()

            # handle case where available_mons is too restricted
            if len(available_mons) <= 5:
                available_mons = self._get_15_nearest(
                    min_popularity, max_popularity, current_team
                )

            # not a creativity related thing but handle mon forms here
            available_mons = [
                mon
                for mon in available_mons
                if not any(
                    mon in team_mon or team_mon in mon for team_mon in current_team
                )
            ]
            return available_mons

    def _get_15_nearest(
        self, min_popularity: float, max_popularity: float, current_team: List[str]
    ):
        mid_bound = (max_popularity - min_popularity) / 2
        format_metadata = self.format_data.format_metadata.copy()
        format_metadata = format_metadata[
            format_metadata["Pokemon"].isin(current_team) == False
        ]
        format_metadata["distance"] = abs(format_metadata["Popularity"] - mid_bound)
        nearest_15_mons = format_metadata.nsmallest(15, "distance")["Pokemon"].tolist()
        return nearest_15_mons

    def _get_min_max_popularity(
        self,
        target_popularity: float,
        remaining_slots: int,
        current_avg_popularity: float,
    ) -> Tuple[float, float]:
        std = self.format_data.top30["Popularity"].std()
        max_popularity = (
            (target_popularity + (0.15) * std * (remaining_slots)) * 6
            - current_avg_popularity * (6 - remaining_slots)
        ) / remaining_slots
        min_popularity = (
            (target_popularity - (0.15) * std * (remaining_slots)) * 6
            - current_avg_popularity * (6 - remaining_slots)
        ) / (remaining_slots)
        return min_popularity, max_popularity

    def _remaining_slots_1(
        self,
        target_avg_popularity: float,
        current_avg_popularity: float,
        limit_lower_popularity: float,
        limit_max_popularity: float,
    ):
        # define the window of popularities that would get us within 2% of the target and return the min, and max
        max_popularity = (target_avg_popularity + 2) * 6 - current_avg_popularity * 5
        min_popularity = (target_avg_popularity - 2) * 6 - current_avg_popularity * 5
        if (
            min_popularity < limit_lower_popularity
            or max_popularity < limit_max_popularity
        ):
            return limit_lower_popularity, limit_max_popularity
        else:
            return min_popularity, max_popularity

    def _get_target_avg_popularity(self) -> float:
        min_popularity, max_popularity = self._get_min_max_target_popularity()
        target_avg_popularity = max_popularity - (self.creativity / 100) * (
            max_popularity - min_popularity
        )
        return target_avg_popularity

    def _get_min_max_target_popularity(self) -> Tuple[float, float]:
        min_popularity = self.format_data.top30["Popularity"].min()
        max_popularity = self.format_data.top30["Popularity"].quantile(0.70)
        return min_popularity, max_popularity

    def _define_popularity_bounds_for_available_pokemon(
        self,
        current_avg_popularity: float,
        target_avg_popularity: float,
        remaining_slots: int,
    ) -> Tuple[float, float]:
        std = self.format_data.top30["Popularity"].std()
        # ---- define lower limits for min and max popularity ----
        lower_limit_popularity = self._get_min_popularity_for_samplesize_limit()
        lower_limit_max_popularity = lower_limit_popularity + 0.5 * std

        # ---- now get bounds ----
        if remaining_slots == 1:
            min_popularity, max_popularity = self._remaining_slots_1(
                target_avg_popularity,
                current_avg_popularity,
                lower_limit_popularity,
                lower_limit_max_popularity,
            )
            return min_popularity, max_popularity
        else:
            # if there is more than 1 slot then we have time to adjust so add a buffer scaled off the std
            min_popularity, max_popularity = self._get_min_max_popularity(
                target_avg_popularity, remaining_slots, current_avg_popularity
            )

            # case: both popularities are too low
            if (
                min_popularity < lower_limit_popularity
                and max_popularity < lower_limit_max_popularity
            ):
                return lower_limit_popularity, lower_limit_max_popularity

            # case: min popularity is too low
            elif min_popularity < lower_limit_popularity:
                return lower_limit_popularity, max_popularity

            # case: max popularity is too low
            elif max_popularity < lower_limit_max_popularity:
                return min_popularity, lower_limit_max_popularity

            # case: both popularities are within bounds
            else:
                return min_popularity, max_popularity

    def _get_min_popularity_for_samplesize_limit(
        self, samplesize_limit: int = 30
    ) -> float:
        return self.format_data.format_metadata[
            self.format_data.format_metadata["SampleSize"] >= samplesize_limit
        ]["Popularity"].min()


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
        creativity_restrictor = CreativityRestrictor(
            creativity=creativity, format_data=self.format_data
        )
        format_mons = self.format_data.get_format_available_mons()
        # handle the case where the current team is empty
        if len(current_team) == 0:
            current_team = [self._pick_random_top30_mon()]

        # solve for remaining mons
        remaining_slots = 6 - len(current_team)
        while remaining_slots > 0:
            current_winrates = winrate_calculator.get_team_winrate_against_meta(
                current_team
            )
            normalized_winrate = winrate_calculator.normalized_winrate(current_winrates)
            available_mons = creativity_restrictor.restrict_available_mons(
                available_mons=format_mons,
                current_team=current_team,
            )
            # remove ignore_mons
            available_mons = [mon for mon in available_mons if mon not in ignore_mons]
            best_mon = self._choose_best_addition(
                available_mons=available_mons,
                current_team=current_team,
                current_norm_winrate=normalized_winrate,
                winrate_calculator=winrate_calculator,
            )
            current_team.append(best_mon)
            remaining_slots -= 1

        return current_team

    def _pick_random_top30_mon(self):
        mon = self.format_data.top30.sample(n=1)["Pokemon"].values[0]
        return mon

    def _choose_best_addition(
        self,
        available_mons: List[str],
        current_team: List[str],
        current_norm_winrate: float,
        winrate_calculator: WinrateCalculator,
    ):
        best_improvement = -100
        best_mon = None
        for mon in available_mons:
            new_team = current_team.copy()
            new_team.append(mon)
            new_winrates = winrate_calculator.get_team_winrate_against_meta(new_team)
            new_norm_winrate = winrate_calculator.normalized_winrate(new_winrates)
            improvement = new_norm_winrate - current_norm_winrate
            if improvement > best_improvement:
                best_improvement = improvement
                best_mon = mon

        return best_mon


class DisplayTeam:
    def __init__(
        self,
        team: List[str],
        engine: str,
        format_data: FormatData,
    ):
        self.team = team
        self.engine = engine
        self.format_data = format_data
        self.top30 = self.format_data.top30
        self.format_metadata = self.format_data.format_metadata

    def get_display_information(self) -> Dict[str, object]:
        display_dict = {
            "team": self.team,
        }
        display_dict["avg_popularity"] = self._get_avg_popularity()
        norm_winrate, winrates = self._get_norm_winrate_and_winrates()
        display_dict["norm_winrate"] = norm_winrate
        display_dict["team info"] = self._add_meta_context_to_winrates(winrates)
        return display_dict

    def _get_avg_popularity(self) -> float:
        avg_popularity = self.format_metadata[
            self.format_metadata["Pokemon"].isin(self.team)
        ]["Popularity"].mean()
        return avg_popularity

    def _get_norm_winrate_and_winrates(self) -> Tuple[float, pd.DataFrame]:
        winrate_calculator = WinrateCalculator(
            format_data=self.format_data, engine_name=self.engine
        )
        winrates = winrate_calculator.get_team_winrate_against_meta(self.team)
        norm_winrate = winrate_calculator.normalized_winrate(winrates)
        return norm_winrate, winrates

    def _add_meta_context_to_winrates(self, winrates: pd.DataFrame) -> pd.DataFrame:
        top30 = self.top30.copy()
        top30 = top30.set_index("Pokemon")
        top30 = top30.drop(columns=["SampleSize", "Format"])
        top30 = top30.rename(columns={"Winrate": "Top30 Base Winrate"})

        winrates = winrates.rename(columns={"winrate": "Team Winrate"})

        context_df = winrates.merge(top30, how="left", on="Pokemon")
        context_df = context_df.reset_index()
        context_df = context_df.rename(
            columns={
                "Pokemon": "Top30 Most Popular Mons",
                "Popularity": "Top30 Mon Popularity (%)",
                "Top30 Base Winrate": "Top30 Mon General Winrate (%)",
                "Team Winrate": "Team Winrate x Top30 Mon (%)",
            }
        )

        # show the highest threats first
        context_df = context_df.sort_values(
            by="Team Winrate x Top30 Mon (%)", ascending=True
        )
        # Round all numeric values to the nearest 1st decimal place (aka all but the Top30 Most Popular Mons column)
        context_df.loc[:, ~context_df.columns.isin(["Top30 Most Popular Mons"])] = (
            context_df.loc[
                :, ~context_df.columns.isin(["Top30 Most Popular Mons"])
            ].round(1)
        )
        return context_df
