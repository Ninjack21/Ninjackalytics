from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta


def contains_mon(row, mon):
    return row.str.contains(mon).any()


def get_top_30_pokemon(battle_format: str):
    ta = TableAccessor()
    metadata = ta.get_pokemonmetadata()
    format_metadata = metadata[metadata["Format"] == battle_format]
    format_metadata = format_metadata.sort_values(by=["Popularity"], ascending=False)
    return format_metadata.head(30)


def get_top_30_winrates_against_team(
    current_team: List[str], top30: List[str], battle_format: str
):
    ta = TableAccessor()
    battle_info = ta.get_battle_info()
    recent_battle_info = battle_info[
        (battle_info["Date_Submitted"] > (datetime.now() - timedelta(days=14)))
        & (battle_info["Format"] == battle_format)
    ]
    teams = ta.get_teams()
    team_ids_for_current_team = set()
    for mon in current_team:
        mon_teams_idx = teams.apply(lambda row: contains_mon(row, mon), axis=1)
        mon_teams = teams[mon_teams_idx]
        new_team_ids = mon_teams["id"].tolist()
        team_ids_for_current_team.update(new_team_ids)

    # these are the battles where a pokemon on the current team was used, so we can get the winrate of this specific
    # combination of pokemon against each of the top 30
    relevant_p1_battles = recent_battle_info[
        (recent_battle_info["P1_team"].isin(team_ids_for_current_team))
    ]
    relevant_p2_battles = recent_battle_info[
        (recent_battle_info["P2_team"].isin(team_ids_for_current_team))
    ]

    winrates = {}
    for mon in top30:
        mon_teams_idx = teams.apply(lambda row: contains_mon(row, mon), axis=1)
        mon_teams = teams[mon_teams_idx]
        mon_wins = 0
        mon_battles = 0
        for team_id in mon_teams["id"]:
            # find the battles where the current mon was on the other team relative to the relevant p1 and p2 battles
            # this will ensure we check battles where the current mon fought against 1 or more of the pokemon on the
            # current team
            mon_in_p2_battles = relevant_p1_battles[
                (relevant_p1_battles["P2_team"] == team_id)
            ]
            mon_in_p1_battles = relevant_p2_battles[
                (relevant_p2_battles["P1_team"] == team_id)
            ]
            all_battles = len(mon_in_p2_battles) + len(mon_in_p1_battles)
            mon_battles += all_battles
            # now calculate the wins for the current mon
            mon_in_p2_wins = len(
                mon_in_p2_battles[
                    mon_in_p2_battles["Winner"] == mon_in_p2_battles["P2"]
                ]
            )
            mon_in_p1_wins = len(
                mon_in_p1_battles[
                    mon_in_p1_battles["Winner"] == mon_in_p1_battles["P1"]
                ]
            )
            mon_wins += mon_in_p2_wins + mon_in_p1_wins

        winrates[mon] = mon_wins / mon_battles

    return pd.DataFrame.from_dict(winrates, orient="index", columns=["winrate"])


def get_format_available_pokemon(battle_format: str) -> List[str]:
    ta = TableAccessor()
    teams = ta.get_teams()
    format_teams = teams[teams["Format"] == battle_format]
    all_mons = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    all_mons = [mon for mon in all_mons if mon != None]
    return all_mons


def normalized_winrate(winrates: pd.DataFrame, battle_format: str) -> pd.DataFrame:
    top30 = get_top_30_pokemon(battle_format)
    # normalize the winrates to be scaled by the popularity of each pokemon while then dividing by the total popularity
    # such that the winrates should sum between 0-100
    top30 = top30.set_index("Pokemon")
    winrates = winrates.join(top30, how="left")
    winrates["Relative Popularity"] = (
        winrates["Popularity"] / winrates["Popularity"].sum()
    )
    winrates["Normalized Winrate"] = (
        winrates["winrate"] * winrates["Relative Popularity"]
    )
    winrates = winrates.drop(columns=["Popularity", "Relative Popularity"])
    # return the overall normalized winrate
    return winrates["Normalized Winrate"].sum()


def get_team_popularity(team: List[str], format_metadata: pd.DataFrame):
    # calculate the current average popularity of the team
    team_popularity = 0
    for mon in team:
        mon_popularity = format_metadata[format_metadata["Pokemon"] == mon][
            "Popularity"
        ].values[0]
        team_popularity += mon_popularity
    team_popularity /= len(team)
    return team_popularity


def get_min_max_target_popularity(format_metadata: pd.DataFrame) -> Tuple[float, float]:
    min_popularity = format_metadata["Popularity"].min()
    max_popularity = format_metadata["Popularity"].quantile(0.5)
    closest_entry = top30.loc[(top30["Popularity"] - max_popularity).abs().idxmin()]
    max_popularity = closest_entry["Popularity"]
    return min_popularity, max_popularity


def get_min_popularity_of_pokemon_with_samplesize_30(
    format_metadata: pd.DataFrame,
) -> float:
    min_data_mons = format_metadata[
        (format_metadata["SampleSize"] >= 30) & (format_metadata["Popularity"] != 0)
    ]
    min_popularity = min_data_mons["Popularity"].min()
    return min_popularity


def define_popularity_bounds_for_available_pokemon(
    current_avg_popularity: float,
    target_avg_popularity: float,
    remaining_slots: int,
    top30: pd.DataFrame,
) -> Tuple[float, float]:
    std = top30["Popularity"].std()
    # we want to define a range of popularity values that we can use to restrict the available pokemon
    # we can use the remaining slots and the std to decide what kind of range of popularity we want to allow
    limit_popularity = self.get_min_popularity_of_pokemon_with_samplesize_30(
        format_metadata
    )
    limit_max_popularity = limit_popularity + 0.5 * std
    if remaining_slots == 1:
        # define the window of popularities that would get us within 2% of the target and return the min, and max
        # now solve for what the final mon's popularity would have to be to be +2% from target and then -2% from target
        max_popularity = (target_avg_popularity + 2) * 6 - current_avg_popularity * 5
        min_popularity = (target_avg_popularity - 2) * 6 - current_avg_popularity * 5
        if min_popularity < limit_popularity or max_popularity < limit_max_popularity:
            return limit_popularity, limit_max_popularity
        else:
            return min_popularity, max_popularity

    else:
        # if there is more than 1 slot then we have time to adjust so add a buffer scaled off the std
        max_popularity = (
            target_avg_popularity + (0.2) * std * (remaining_slots)
        ) - current_avg_popularity * (6 - remaining_slots)
        min_popularity = (
            target_avg_popularity - (0.2) * std * (remaining_slots)
        ) - current_avg_popularity * (6 - remaining_slots)
        if min_popularity < limit_popularity and max_popularity < limit_max_popularity:
            return limit_popularity, limit_max_popularity
        elif min_popularity < limit_popularity:
            return limit_popularity, max_popularity
        elif max_popularity < limit_max_popularity:
            return min_popularity, limit_max_popularity
        else:
            return min_popularity, max_popularity


def restrict_available_mons_based_on_creativity(
    current_team: List[str], creativity: int
):
    """
    creativity will be an int between 0-100, and we want to create a way to say more creative teams
    have a lower overall popularity.

    we want to have creativity increases reduce some kind of normalized overall popularity of the team. we can have
    it look at the current average popularity. Then we can look at the current distributions of mon popularities
    within the format_metadata.

    we can use the max popularity to get a feel for how evenly or unevently distributed the popularities are. perhaps
    the spread within the top30 is a good way to measure this.

    take a percentage of the overall spread. if a spread is very large and creativity is large then this means the
    """
    all_mons = get_format_available_pokemon(battle_format)
    ta = TableAccessor()
    metadata = ta.get_pokemonmetadata()
    format_metadata = metadata[metadata["Format"] == battle_format]
    format_metadata = format_metadata.sort_values(by=["Popularity"], ascending=False)
    top30 = format_metadata.head(30)
    min_popularity, max_popularity = get_min_max_target_popularity(format_metadata)
    # use creativity percent to move [creativity %] of the way down from max to min popularity to get target avg
    creativity_percent = creativity / 100
    target_avg_popularity = max_popularity - creativity_percent * (
        max_popularity - min_popularity
    )

    current_avg_popularity = get_team_popularity(current_team, format_metadata)
    remaining_slots = 6 - len(current_team)
    min_popularity, max_popularity = define_popularity_bounds_for_available_pokemon(
        current_avg_popularity=current_avg_popularity,
        target_avg_popularity=target_avg_popularity,
        remaining_slots=remaining_slots,
        top30=top30,
    )
    available_pokemon = [
        mon
        for mon in all_mons
        if min_popularity
        <= format_metadata[format_metadata["Pokemon"] == mon]["Popularity"].values[0]
        <= max_popularity
    ]

    return available_pokemon


def solve_for_remainder_of_team(
    current_team: List[str],
    battle_format: str,
    creativity: int,
    disregard_pokemon: List[str] = [],
):
    top30 = get_top_30_pokemon(battle_format)
    top30 = top30["Pokemon"].tolist()

    remaining_slots = 6 - len(current_team)
    while remaining_slots > 0:
        # ---- calc the current winrates and available mons -----
        current_winrates = get_top_30_winrates_against_team(
            current_team=current_team,
            top30=top30,
            battle_format=battle_format,
        )
        current_norm_winrate = normalized_winrate(current_winrates, battle_format)
        available_pokemon = get_format_available_pokemon(battle_format)
        available_pokemon = restrict_available_mons_based_on_creativity(
            current_team=current_team,
            creativity=creativity,
        )
        available_pokemon = [
            mon
            for mon in available_pokemon
            if mon not in disregard_pokemon and mon not in current_team
        ]
        # --------- now look for the next best pokemon to add -------
        # now we can try adding each individual pokemon to see who improves the winrate the most
        best_improvement = -100
        best_mon = None
        for mon in available_pokemon:
            new_team = current_team.copy()
            new_team.append(mon)
            new_winrates = get_top_30_winrates_against_team(
                current_team=new_team,
                top30=top30,
                battle_format=battle_format,
            )
            improvement = normalized_winrate(new_winrates) - current_norm_winrate
            if improvement > best_improvement:
                best_improvement = improvement
                best_mon = mon

        # update the current team with the best improvement mon
        current_team.append(best_mon)
        remaining_slots -= 1

    current_avg_popularity = get_team_popularity(current_team, format_metadata)
    current_winrates = get_top_30_winrates_against_team(
        current_team=current_team,
        top30=top30,
        battle_format=battle_format,
    )
    current_norm_winrate = normalized_winrate(current_winrates, battle_format)
    return (
        current_team,
        current_avg_popularity,
        target_avg_popularity,
        current_norm_winrate,
    )
