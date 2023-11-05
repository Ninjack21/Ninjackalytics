from typing import Dict, List, Tuple
import dash
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.io as pio
from ninjackalytics.services.database_interactors import (
    BattleDataRetriever,
    BattleDataUploader,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon

# make all graphs plotly_dark by default
pio.templates.default = "plotly_dark"

# ========= UTILITY FUNCTIONS =========


def get_total_number_of_turns(battle_data: Dict[str, pd.DataFrame]) -> int:
    actions = battle_data["actions"]
    return actions["Turn"].max()


def parse_and_return_battle_data(battle_id):
    retriever = BattleDataRetriever()
    exists = retriever.check_if_battle_exists(battle_id)
    if not exists:
        try:
            battle = Battle(f"https://replay.pokemonshowdown.com/{battle_id}")
            pokemon = BattlePokemon(battle)
            parser = BattleParser(battle, pokemon)
            parser.analyze_battle()
            uploader = BattleDataUploader()
            uploader.upload_battle(parser)
        except Exception as e:
            return None
    battle_data = retriever.get_battle_data(battle_id)
    return battle_data


def get_winner_pnum(battle_data: Dict[str, pd.DataFrame]) -> int:
    battle_info = battle_data["battle_info"]
    winner = battle_info["Winner"].iloc[0]
    winner_pnum = 1 if winner == battle_info["P1"].iloc[0] else 2
    return winner_pnum


def get_winner_loser_names(battle_data: Dict[str, pd.DataFrame]) -> Tuple[str, str]:
    battle_info = battle_data["battle_info"]
    winner = battle_info["Winner"].iloc[0]
    winner_name = (
        battle_info["P1"].iloc[0]
        if winner == battle_info["P1"].iloc[0]
        else battle_info["P2"].iloc[0]
    )
    loser_name = (
        battle_info["P2"].iloc[0]
        if winner == battle_info["P1"].iloc[0]
        else battle_info["P1"].iloc[0]
    )
    return winner_name, loser_name


def generate_hp_discrepancy_df(
    battle_data: Dict[str, pd.DataFrame],
    selected_winner_actions: List[str],
    selected_loser_actions: List[str],
    selected_healing_source_names: List[str],
    selected_healing_receivers: List[str],
    selected_dmg_source_names: List[str],
    selected_dmg_dealers: List[str],
    selected_turns: List[int],
    selected_damage_types: List[str],
    selected_healing_types: List[str],
):
    battle_info = battle_data["battle_info"]
    teams = battle_data["teams"]
    damages = battle_data["damages"]
    healing = battle_data["healing"]
    winner_pnum = get_winner_pnum(battle_data)

    # filter damages and healing for the selected types
    if selected_damage_types:
        damages = damages[damages["Type"].isin(selected_damage_types)]
    if selected_healing_types:
        healing = healing[healing["Type"].isin(selected_healing_types)]
    if selected_turns:
        damages = damages[damages["Turn"].isin(selected_turns)]
        healing = healing[healing["Turn"].isin(selected_turns)]
    if selected_dmg_dealers:
        damages = damages[damages["Dealer"].isin(selected_dmg_dealers)]
    if selected_dmg_source_names:
        damages = damages[damages["Source_Name"].isin(selected_dmg_source_names)]
    if selected_healing_receivers:
        healing = healing[healing["Receiver"].isin(selected_healing_receivers)]
    if selected_healing_source_names:
        healing = healing[healing["Source_Name"].isin(selected_healing_source_names)]
    if selected_winner_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_winner_actions,
            player_number=winner_pnum,
        )
        damages = damages[damages["Turn"].isin(action_turns)]
        healing = healing[healing["Turn"].isin(action_turns)]
    if selected_loser_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_loser_actions,
            player_number=(1 if winner_pnum == 2 else 2),
        )
        damages = damages[damages["Turn"].isin(action_turns)]
        healing = healing[healing["Turn"].isin(action_turns)]

    # determine starting hp discrepancy (normally 0)
    if winner_pnum == 1:
        winner_team_id = battle_info["P1_team"].iloc[0]
        loser_team_id = battle_info["P2_team"].iloc[0]
    else:
        winner_team_id = battle_info["P2_team"].iloc[0]
        loser_team_id = battle_info["P1_team"].iloc[0]

    winner_team = teams[teams["id"] == winner_team_id]
    loser_team = teams[teams["id"] == loser_team_id]

    winner_n_mons = winner_team.notnull().sum(axis=1).values[0]
    loser_n_mons = loser_team.notnull().sum(axis=1).values[0]

    starting_mons_diff = winner_n_mons - loser_n_mons

    initial_hp_diff = starting_mons_diff * 100  # all begin with 100% hp
    cumulative_hp_discrepancy = initial_hp_diff

    # build new df which tracks the hp discrepancy over the course of the battle
    # we will use the turn number as the index
    df = pd.DataFrame()
    all_turns = pd.concat([damages["Turn"], healing["Turn"]]).unique()
    all_turns.sort()

    for turn in all_turns:
        # filter damages and healing for the current turn
        damages_turn = damages[damages["Turn"] == turn]
        healing_turn = healing[healing["Turn"] == turn]

        # calculate the total hp change for each player on each action that took place
        # will associate positive values with the winner and negative values with the loser
        winner_dmgs = damages_turn[
            damages_turn["Receiver_Player_Number"] != winner_pnum
        ]
        loser_dmgs = damages_turn[damages_turn["Receiver_Player_Number"] == winner_pnum]

        winner_heals = healing_turn[
            healing_turn["Receiver_Player_Number"] == winner_pnum
        ]
        loser_heals = healing_turn[
            healing_turn["Receiver_Player_Number"] != winner_pnum
        ]

        winner_hp_change = winner_dmgs["Damage"].sum() + winner_heals["Healing"].sum()
        loser_hp_change = loser_dmgs["Damage"].sum() + loser_heals["Healing"].sum()

        net_hp_change = winner_hp_change - loser_hp_change

        # add the net hp change to the initial hp discrepancy
        cumulative_hp_discrepancy += net_hp_change

        turn_df = pd.DataFrame(
            {
                "Turn": [turn],
                "HP Discrepancy": [cumulative_hp_discrepancy],
            }
        )

        # add the net hp change to the df
        df = pd.concat([df, turn_df], ignore_index=True)

    return df


def get_turns_associated_with_action_types(
    battle_data: Dict[str, pd.DataFrame],
    selected_actions: List[str],
    player_number: int,
) -> List[int]:
    actions = battle_data["actions"]
    if selected_actions:
        actions = actions[
            (actions["Action"].isin(selected_actions))
            & (actions["Player_Number"] == player_number)
        ]
    return actions["Turn"].unique().tolist()


# ========= FIGURE GENERATING FUNCTIONS =========


def generate_damages_figures(
    battle_data: Dict[str, pd.DataFrame],
    selected_winner_actions: List[str],
    selected_loser_actions: List[str],
    selected_dmg_source_names: List[str],
    selected_dmg_dealers: List[str],
    selected_turns: List[int],
    selected_damage_types: List[str],
) -> Tuple[go.Figure, go.Figure]:
    winner_pnum = get_winner_pnum(battle_data)
    winner, loser = get_winner_loser_names(battle_data)

    damages = battle_data["damages"]
    # create a color mapping for the damage types
    damage_types = damages["Type"].unique()
    damage_type_colors = {}
    for i, damage_type in enumerate(damage_types):
        damage_type_colors[damage_type] = px.colors.qualitative.D3[i]

    damages["Color"] = damages["Type"].map(damage_type_colors)

    # apply filtering
    if selected_damage_types:
        damages = damages[damages["Type"].isin(selected_damage_types)]

    if selected_turns:
        damages = damages[damages["Turn"].isin(selected_turns)]

    if selected_dmg_dealers:
        damages = damages[damages["Dealer"].isin(selected_dmg_dealers)]

    if selected_dmg_source_names:
        damages = damages[damages["Source_Name"].isin(selected_dmg_source_names)]

    if selected_winner_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_winner_actions,
            player_number=winner_pnum,
        )
        damages = damages[damages["Turn"].isin(action_turns)]

    if selected_loser_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_loser_actions,
            player_number=(1 if winner_pnum == 2 else 2),
        )
        damages = damages[damages["Turn"].isin(action_turns)]

    # Filter the damages data for each player
    # NOTE: the winner damages are those damages dealt to the receiver whose player number IS NOT winner_pnum
    winner_damages = damages[damages["Receiver_Player_Number"] != winner_pnum]
    loser_damages = damages[damages["Receiver_Player_Number"] == winner_pnum]

    # Aggregate the data by 'Dealer' and 'Type', summing 'Damage'
    winner_damages_agg = (
        winner_damages.groupby(["Dealer", "Type"])["Damage"].sum().reset_index()
    )
    loser_damages_agg = (
        loser_damages.groupby(["Dealer", "Type"])["Damage"].sum().reset_index()
    )

    # Create the bar charts
    fig_p1 = go.Figure()
    fig_p2 = go.Figure()

    for damage_type in damage_types:
        # Filter the aggregated damages data for the current damage type
        winner_damages_type = winner_damages_agg[
            winner_damages_agg["Type"] == damage_type
        ]
        loser_damages_type = loser_damages_agg[loser_damages_agg["Type"] == damage_type]

        # Add a bar to the charts for the current damage type
        fig_p1.add_trace(
            go.Bar(
                y=winner_damages_type["Dealer"],
                x=winner_damages_type["Damage"],
                orientation="h",
                marker=dict(color=damage_type_colors[damage_type]),
                name=damage_type,  # Use the damage type as the name
                showlegend=True,
            )
        )
        fig_p2.add_trace(
            go.Bar(
                y=loser_damages_type["Dealer"],
                x=loser_damages_type["Damage"],
                orientation="h",
                marker=dict(color=damage_type_colors[damage_type]),
                name=damage_type,  # Use the damage type as the name
                showlegend=True,
            )
        )

    # Set the layout for the graphs
    fig_p1.update_layout(
        title=f"{winner} Damage Chart<br>Total % HP Dealt = {winner_damages['Damage'].sum()}",
        xaxis_title="% HP Damage Dealt",
        yaxis_title="Dealer",
    )
    fig_p2.update_layout(
        title=f"{loser} Damage Chart<br>Total % HP Dealt = {loser_damages['Damage'].sum()}",
        xaxis_title="% HP Damage Dealt",
        yaxis_title="Dealer",
    )

    return fig_p1, fig_p2


def generate_hp_discrepancy_figure(
    battle_data: Dict[str, pd.DataFrame],
    selected_winner_actions: List[str],
    selected_loser_actions: List[str],
    selected_healing_source_names: List[str],
    selected_healing_receivers: List[str],
    selected_dmg_source_names: List[str],
    selected_dmg_dealers: List[str],
    selected_turns: List[int],
    selected_damage_types: List[str],
    selected_healing_types: List[str],
) -> go.Figure:
    winner, loser = get_winner_loser_names(battle_data)

    hp_discrepancy_df = generate_hp_discrepancy_df(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_healing_source_names=selected_healing_source_names,
        selected_healing_receivers=selected_healing_receivers,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=selected_turns,
        selected_damage_types=selected_damage_types,
        selected_healing_types=selected_healing_types,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hp_discrepancy_df["Turn"],
            y=hp_discrepancy_df["HP Discrepancy"],
            mode="lines+markers",
            line=dict(color="lightgray"),  # set a single color for all lines
            marker=dict(
                color=[
                    "red" if x <= 0 else "green"
                    for x in hp_discrepancy_df["HP Discrepancy"]
                ],
                size=8,
            ),
            name="% HP Discrepancy",
        )
    )
    fig.update_layout(
        title=f"HP Discrepancy Across Battle<br>Positive Values = {winner} Advantage, Negative Values = {loser} Advantage",
        xaxis_title="Turn",
        yaxis_title="% HP Discrepancy",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )

    return fig


def generate_healing_figures(
    battle_data: Dict[str, pd.DataFrame],
    selected_winner_actions: List[str],
    selected_loser_actions: List[str],
    selected_healing_source_names: List[str],
    selected_healing_receivers: List[str],
    selected_turns: List[int],
    selected_healing_types: List[str],
) -> Tuple[go.Figure, go.Figure]:
    winner_pnum = get_winner_pnum(battle_data)
    winner, loser = get_winner_loser_names(battle_data)

    healing = battle_data["healing"]
    # create a color mapping for the healing types
    healing_types = healing["Type"].unique()
    healing_type_colors = {}
    for i, healing_type in enumerate(healing_types):
        healing_type_colors[healing_type] = px.colors.qualitative.D3[i]

    healing["Color"] = healing["Type"].map(healing_type_colors)

    # apply filtering
    if selected_healing_types:
        healing = healing[healing["Type"].isin(selected_healing_types)]
    if selected_turns:
        healing = healing[healing["Turn"].isin(selected_turns)]
    if selected_healing_receivers:
        healing = healing[healing["Receiver"].isin(selected_healing_receivers)]
    if selected_healing_source_names:
        healing = healing[healing["Source_Name"].isin(selected_healing_source_names)]
    if selected_winner_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_winner_actions,
            player_number=winner_pnum,
        )
        healing = healing[healing["Turn"].isin(action_turns)]
    if selected_loser_actions:
        action_turns = get_turns_associated_with_action_types(
            battle_data=battle_data,
            selected_actions=selected_loser_actions,
            player_number=(1 if winner_pnum == 2 else 2),
        )
        healing = healing[healing["Turn"].isin(action_turns)]

    # Filter the healing data for each player
    winner_healing = healing[healing["Receiver_Player_Number"] == winner_pnum]
    loser_healing = healing[healing["Receiver_Player_Number"] != winner_pnum]

    # Aggregate the data by 'Source_Name' and 'Type', summing 'Healing'
    winner_healing_agg = (
        winner_healing.groupby(["Receiver", "Source_Name", "Type"])["Healing"]
        .sum()
        .reset_index()
    )
    loser_healing_agg = (
        loser_healing.groupby(["Receiver", "Source_Name", "Type"])["Healing"]
        .sum()
        .reset_index()
    )

    # Create the bar charts
    fig_p1 = go.Figure()
    fig_p2 = go.Figure()

    for healing_type in healing_types:
        # Filter the aggregated healing data for the current healing type
        winner_healing_type = winner_healing_agg[
            winner_healing_agg["Type"] == healing_type
        ]
        loser_healing_type = loser_healing_agg[
            loser_healing_agg["Type"] == healing_type
        ]

        # Add a bar to the charts for the current healing type
        fig_p1.add_trace(
            go.Bar(
                y=winner_healing_type["Receiver"],
                x=winner_healing_type["Healing"],
                orientation="h",
                marker=dict(color=healing_type_colors[healing_type]),
                name=healing_type,  # Use the healing type as the name
                showlegend=True,
            )
        )
        fig_p2.add_trace(
            go.Bar(
                y=loser_healing_type["Receiver"],
                x=loser_healing_type["Healing"],
                orientation="h",
                marker=dict(color=healing_type_colors[healing_type]),
                name=healing_type,  # Use the healing type as the name
                showlegend=True,
            )
        )

    # Set the layout for the graphs
    fig_p1.update_layout(
        title=f"{winner} Healing Chart<br>Total % HP Healed = {winner_healing['Healing'].sum()}",
        xaxis_title="% HP Healing",
        yaxis_title="Source Name",
    )
    fig_p2.update_layout(
        title=f"{loser} Healing Chart<br>Total % HP Healed = {loser_healing['Healing'].sum()}",
        xaxis_title="% HP Healing",
        yaxis_title="Source Name",
    )

    return fig_p1, fig_p2


def generate_action_choices_pie_chart(
    battle_data: Dict[str, pd.DataFrame],
    selected_turns: List[int],
    selected_winner_actions: List[str],
    selected_loser_actions: List[str],
) -> Tuple[go.Figure, go.Figure]:
    actions_df = battle_data["actions"]
    winner_pnum = get_winner_pnum(battle_data)
    winner_name, loser_name = get_winner_loser_names(battle_data)

    if selected_turns:
        actions_df = actions_df[actions_df["Turn"].isin(selected_turns)]

    winner_actions_df = actions_df[actions_df["Player_Number"] == winner_pnum]
    loser_actions_df = actions_df[actions_df["Player_Number"] != winner_pnum]

    if selected_winner_actions:
        winner_actions_df = winner_actions_df[
            (winner_actions_df["Action"].isin(selected_winner_actions))
            & (winner_actions_df["Player_Number"] == winner_pnum)
        ]
    if selected_loser_actions:
        loser_actions_df = loser_actions_df[
            (loser_actions_df["Action"].isin(selected_loser_actions))
            & (loser_actions_df["Player_Number"] != winner_pnum)
        ]

    winner_actions = winner_actions_df["Action"].value_counts()
    loser_actions = loser_actions_df["Action"].value_counts()

    winner_fig = go.Figure(
        data=[go.Pie(labels=winner_actions.index, values=winner_actions.values)]
    )
    winner_fig.update_layout(title=f"{winner_name}'s Actions")

    loser_fig = go.Figure(
        data=[go.Pie(labels=loser_actions.index, values=loser_actions.values)]
    )
    loser_fig.update_layout(title=f"{loser_name}'s Actions")

    return winner_fig, loser_fig


def generate_damage_per_entrance_figures(
    battle_data: Dict[str, pd.DataFrame]
) -> Tuple[go.Figure, go.Figure]:
    damages = battle_data["damages"]
    pivots = battle_data["pivots"]
    print(pivots.columns)
    winner_pnum = get_winner_pnum(battle_data)

    winner_pokemon = pivots["Pokemon_Enter"][
        pivots["Player_Number"] == winner_pnum
    ].unique()
    loser_pokemon = pivots["Pokemon_Enter"][
        pivots["Player_Number"] != winner_pnum
    ].unique()

    winner_dmg_per_entrance = []
    for pokemon in winner_pokemon:
        pokemon_dmg = (
            damages["Damage"]
            .loc[
                (damages["Dealer"] == pokemon)
                & (damages["Player_Number"] != winner_pnum)
            ]
            .sum()
        )
        pokemon_entrances = (
            pivots["Turn"]
            .loc[
                (pivots["Pokemon_Enter"] == pokemon)
                & (pivots["Player_Number"] == winner_pnum),
            ]
            .nunique()
        )
        if pokemon_entrances > 0:
            winner_dmg_per_entrance.append(pokemon_dmg / pokemon_entrances)

    loser_dmg_per_entrance = []
    for pokemon in loser_pokemon:
        pokemon_dmg = (
            damages["Damage"]
            .loc[
                (damages["Attacker_Pokemon"] == pokemon)
                & (damages["Player_Number"] == winner_pnum),
            ]
            .sum()
        )
        pokemon_entrances = (
            pivots["Turn"]
            .loc[
                (pivots["Pokemon_Enter"] == pokemon)
                & (pivots["Player_Number"] != winner_pnum),
            ]
            .nunique()
        )
        if pokemon_entrances > 0:
            loser_dmg_per_entrance.append(pokemon_dmg / pokemon_entrances)

    winner_fig = go.Figure(
        data=[
            go.Bar(
                x=winner_dmg_per_entrance,
                y=winner_pokemon,
                orientation="h",
                name="Average Damage per Entrance",
            )
        ]
    )
    winner_fig.update_layout(
        title="Pokemon Average Damage per Entrance",
        xaxis_title="Average Damage per Entrance",
        yaxis_title="Pokemon",
    )

    loser_fig = go.Figure(
        data=[
            go.Bar(
                x=loser_dmg_per_entrance,
                y=loser_pokemon,
                orientation="h",
                name="Average Damage per Entrance",
            )
        ]
    )
    loser_fig.update_layout(
        title="Pokemon Average Damage per Entrance",
        xaxis_title="Average Damage per Entrance",
        yaxis_title="Pokemon",
    )

    return winner_fig, loser_fig
