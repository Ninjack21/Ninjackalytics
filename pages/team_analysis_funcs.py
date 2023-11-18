from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta
from tqdm import tqdm


# ----------- utility functions ----------------
def get_viable_formats():
    ta = TableAccessor()
    battle_info = ta.get_battle_info()
    viable_formats = battle_info["Format"].unique()
    return viable_formats


def get_viable_format_pokemon(selected_format: str) -> List[str]:
    if selected_format == None:
        return []

    format_info = get_format_battle_info(battle_format=selected_format)
    format_teams = get_format_teams(format_battle_info=format_info)
    # now get the pokemon from the teams
    viable_pokemon = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    # now remove any nulls
    viable_pokemon = [mon for mon in viable_pokemon if mon != None]
    return viable_pokemon


def get_viable_pokemon(
    selected_format: str, selected_ignore_mons: List[str], already_used_mons: List[str]
):
    if selected_format == None:
        return []
    unavailable_mons = [None]
    if already_used_mons:
        unavailable_mons += already_used_mons
    if selected_ignore_mons:
        unavailable_mons += selected_ignore_mons

    format_info = get_format_battle_info(battle_format=selected_format)
    format_teams = get_format_teams(format_battle_info=format_info)
    # now get the pokemon from the teams
    viable_pokemon = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    viable_pokemon = [mon for mon in viable_pokemon if mon not in unavailable_mons]
    return viable_pokemon


# ------------ do sql queries once with these functions --------------------
def get_format_battle_info(battle_format: str):
    ta = TableAccessor()
    battle_info = ta.get_battle_info()
    format_info = battle_info[battle_info["Format"] == battle_format]
    return format_info


def get_format_metadata(battle_format: str):
    ta = TableAccessor()
    metadata = ta.get_pokemonmetadata()
    format_metadata = metadata[metadata["Format"] == battle_format]
    return format_metadata


def get_format_teams(format_battle_info: pd.DataFrame):
    ta = TableAccessor()
    teams = ta.get_teams()
    team_ids = pd.concat(
        [format_battle_info["P1_team"], format_battle_info["P2_team"]]
    ).unique()
    format_teams = teams[teams["id"].isin(team_ids)]
    return format_teams


def get_pvpmetadata():
    ta = TableAccessor()
    pvpmetadata = ta.get_pvpmetadata()
    return pvpmetadata


# ----------- now utilize utility functions with dataframes passed around ------------


def contains_mon(row, mon):
    return row.str.contains(mon).any()


def get_team_ids_for_mons(format_teams: pd.DataFrame, mons: List[str]):
    team_ids_for_mons = set()
    for mon in mons:
        mon_teams_idx = format_teams.apply(lambda row: contains_mon(row, mon), axis=1)
        mon_teams = format_teams[mon_teams_idx]
        new_team_ids = mon_teams["id"].tolist()
        team_ids_for_mons.update(new_team_ids)
    return team_ids_for_mons


def get_team_winrates_against_top_30(
    current_team: List[str],
    top30mons: List[str],
    format_pvp: pd.DataFrame,
):
    # the aim is to calculate how the team would do against the top30 mons, so we want to calculate the expected
    # winrate against each of the top30 mons by using the sample sizes and winrates of each of the mons on our
    # team to create the aggregate expected winrate against each of the top30 mons
    winrates = {}
    pvps = format_pvp[
        (format_pvp["Pokemon1"].isin(current_team))
        & (format_pvp["Pokemon2"].isin(top30mons))
    ]

    for mon in top30mons:
        # this gets our winrate into each of the top 30
        team_wr_into_mon = pvps[
            pvps["Pokemon1"].isin(current_team) & (pvps["Pokemon2"] == mon)
        ].copy()  # create a copy of the slice to avoid SettingWithCopyWarning
        total_samplesize = team_wr_into_mon["SampleSize"].sum()
        if total_samplesize == 0:
            # if no data, suggests highly off meta so assume 40% winrate
            winrates[mon] = 40
            continue
        else:
            team_wr_into_mon["Weighted Winrate"] = (
                team_wr_into_mon["Winrate"]
                * team_wr_into_mon["SampleSize"]
                / total_samplesize
            )
            winrate = team_wr_into_mon["Weighted Winrate"].sum()
            winrates[mon] = winrate

    winrates = pd.DataFrame.from_dict(winrates, orient="index", columns=["winrate"])
    return winrates


def normalized_winrate(winrates: pd.DataFrame, top30: pd.DataFrame) -> pd.DataFrame:
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


# ----------- handle the available pokemon rules ----------------
def get_format_available_pokemon(
    format_teams: pd.DataFrame, format_metadata: pd.DataFrame
) -> List[str]:
    all_mons = pd.concat([format_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    all_mons = [mon for mon in all_mons if mon != None]
    # restrict mons to only those seen within the format_metadata
    all_mons = [mon for mon in all_mons if mon in format_metadata["Pokemon"].tolist()]
    # now handle sample size of 20 limit
    all_mons = [
        mon
        for mon in all_mons
        if format_metadata[format_metadata["Pokemon"] == mon]["SampleSize"].values[0]
        >= 20
    ]
    return all_mons


def restrict_available_mons_based_on_creativity(
    all_mons: List[str],
    current_team: List[str],
    format_metadata: pd.DataFrame,
    top30: pd.DataFrame,
    creativity: int,
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
    if creativity == 0:
        return all_mons
    target_avg_popularity = get_target_avg_popularity(
        top30=top30, creativity=creativity
    )

    current_avg_popularity = get_team_popularity(current_team, format_metadata)
    remaining_slots = 6 - len(current_team)
    min_popularity, max_popularity = define_popularity_bounds_for_available_pokemon(
        current_avg_popularity=current_avg_popularity,
        target_avg_popularity=target_avg_popularity,
        remaining_slots=remaining_slots,
        top30=top30,
        format_metadata=format_metadata,
    )
    available_pokemon = []
    for mon in all_mons:
        mon = format_metadata[format_metadata["Pokemon"] == mon].iloc[0]
        if mon["Popularity"] >= min_popularity and mon["Popularity"] <= max_popularity:
            available_pokemon.append(mon["Pokemon"])

    return available_pokemon


def get_min_max_target_popularity(top30: pd.DataFrame) -> Tuple[float, float]:
    min_popularity = top30["Popularity"].min()
    max_popularity = top30["Popularity"].quantile(0.5)
    return min_popularity, max_popularity


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


def define_popularity_bounds_for_available_pokemon(
    current_avg_popularity: float,
    target_avg_popularity: float,
    remaining_slots: int,
    top30: pd.DataFrame,
    format_metadata: pd.DataFrame,
) -> Tuple[float, float]:
    std = top30["Popularity"].std()
    # we want to define a range of popularity values that we can use to restrict the available pokemon
    # we can use the remaining slots and the std to decide what kind of range of popularity we want to allow
    limit_popularity = get_min_popularity_of_pokemon_with_samplesize(
        format_metadata=format_metadata, sample_size=20
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
            (target_avg_popularity + (0.1) * std * (remaining_slots)) * 6
            - current_avg_popularity * (6 - remaining_slots)
        ) / remaining_slots
        min_popularity = (
            (target_avg_popularity - (0.1) * std * (remaining_slots)) * 6
            - current_avg_popularity * (6 - remaining_slots)
        ) / (remaining_slots)

        if min_popularity < limit_popularity and max_popularity < limit_max_popularity:
            return limit_popularity, limit_max_popularity
        elif min_popularity < limit_popularity:
            return limit_popularity, max_popularity
        elif max_popularity < limit_max_popularity:
            return min_popularity, limit_max_popularity
        else:
            return min_popularity, max_popularity


def get_min_popularity_of_pokemon_with_samplesize(
    format_metadata: pd.DataFrame, sample_size: int
) -> float:
    min_data_mons = format_metadata[
        (format_metadata["SampleSize"] >= sample_size)
        & (format_metadata["Popularity"] != 0)
    ]
    min_popularity = min_data_mons["Popularity"].min()
    return min_popularity


def get_target_avg_popularity(top30: pd.DataFrame, creativity: int) -> float:
    min_popularity, max_popularity = get_min_max_target_popularity(top30=top30)
    target_avg_popularity = max_popularity - (creativity / 100) * (
        max_popularity - min_popularity
    )
    return target_avg_popularity


# ----------- now solve for the team ----------------


def solve_for_remainder_of_team(
    current_team: List[str],
    battle_format: str,
    creativity: int,
    disregard_pokemon: List[str] = [],
):
    format_metadata = get_format_metadata(battle_format)
    top30 = format_metadata.sort_values(by="Popularity", ascending=False).head(30)
    format_info = get_format_battle_info(battle_format)
    format_teams = get_format_teams(format_info)
    pvpmetadata = get_pvpmetadata()
    f_pvpmetadata = pvpmetadata[pvpmetadata["Format"] == battle_format]
    remaining_slots = 6 - len(current_team)
    while remaining_slots > 0:
        current_winrates = get_team_winrates_against_top_30(
            current_team=current_team,
            top30mons=top30["Pokemon"].tolist(),
            format_pvp=f_pvpmetadata,
        )
        current_norm_winrate = normalized_winrate(
            winrates=current_winrates, top30=top30
        )
        available_pokemon = get_format_available_pokemon(
            format_teams=format_teams, format_metadata=format_metadata
        )
        available_pokemon = restrict_available_mons_based_on_creativity(
            all_mons=available_pokemon,
            current_team=current_team,
            format_metadata=format_metadata,
            top30=top30,
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
        for mon in tqdm(available_pokemon):
            new_team = current_team.copy()
            new_team.append(mon)
            new_winrates = get_team_winrates_against_top_30(
                current_team=new_team,
                top30mons=top30["Pokemon"].tolist(),
                format_pvp=f_pvpmetadata,
            )
            improvement = (
                normalized_winrate(
                    winrates=new_winrates,
                    top30=top30,
                )
                - current_norm_winrate
            )
            if improvement > best_improvement:
                best_improvement = improvement
                best_mon = mon

        # update the current team with the best improvement mon
        current_team.append(best_mon)
        remaining_slots -= 1

    current_avg_popularity = get_team_popularity(
        team=current_team,
        format_metadata=format_metadata,
    )
    current_winrates = get_team_winrates_against_top_30(
        current_team=current_team,
        top30mons=top30["Pokemon"].tolist(),
        format_pvp=f_pvpmetadata,
    )
    current_norm_winrate = normalized_winrate(
        winrates=current_winrates,
        top30=top30,
    )
    target_avg_popularity = get_target_avg_popularity(
        top30=top30, creativity=creativity
    )
    solved_team_data = {
        "team": current_team,
        "avg_popularity": current_avg_popularity,
        "norm_winrate": current_norm_winrate,
        "target_avg_popularity": target_avg_popularity,
        "top30_winrates": current_winrates,
    }
    return solved_team_data
