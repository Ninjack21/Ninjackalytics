from pages.page_utilities.general_utility import (
    DatabaseData,
    FormatData,
    WinrateCalculator,
)
import pandas as pd
from typing import List, Tuple, Dict
import multiprocessing
from multiprocessing import Pool
from functools import partial
import psutil


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

        partial_calc_improvement = partial(
            self._calculate_improvement,
            current_team,
            current_norm_winrate,
            winrate_calculator,
        )

        # Use multiprocessing to calculate improvements for all available mons
        num_processors = self._get_optimal_process_count()
        with Pool(processes=num_processors) as pool:
            results = pool.map(partial_calc_improvement, available_mons)

        # Find the mon with the maximum improvement
        best_improvement, best_mon = max(results, key=lambda x: x[0])

        return best_mon

    def _calculate_improvement(
        self, current_team, current_norm_winrate, winrate_calculator, mon
    ):
        """
        Calculate the improvement for adding a single Pokémon to the current team.
        Returns a tuple of (improvement, mon).
        """
        new_team = current_team + [mon]
        new_winrates = winrate_calculator.get_team_winrate_against_meta(new_team)
        new_norm_winrate = winrate_calculator.normalized_winrate(new_winrates)
        improvement = new_norm_winrate - current_norm_winrate
        return (improvement, mon)

    def _get_optimal_process_count(self):
        cpu_usage = psutil.cpu_percent()
        n_processors = multiprocessing.cpu_count()
        free_processors = n_processors - len(multiprocessing.active_children())
        if cpu_usage < 50:
            return round(free_processors * 0.75)
        elif cpu_usage < 75:
            return round(free_processors * 0.5)
        else:
            return max(round(free_processors * 0.25), 1)


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
