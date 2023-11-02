from typing import Dict, List
import dash
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from ninjackalytics.services.database_interactors import (
    BattleDataRetriever,
    BattleDataUploader,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon

import os

os.environ["FLASK_ENV"] = "testing"

retriever = BattleDataRetriever()


def parse_and_return_battle_data(battle_id):
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


def generate_damages_figures(
    battle_data: Dict[str, pd.DataFrame], selected_damage_types: List[str]
) -> dbc.Row:
    damages = battle_data["damages"]
    # create a color mapping for the damage types
    damage_types = damages["Type"].unique()
    damage_type_colors = {}
    for i, damage_type in enumerate(damage_types):
        damage_type_colors[damage_type] = px.colors.qualitative.D3[i]

    damages["Color"] = damages["Type"].map(damage_type_colors)

    # Filter the damages data for each player
    damages_p1 = damages[damages["Receiver_Player_Number"] == 2]
    damages_p2 = damages[damages["Receiver_Player_Number"] == 1]

    if selected_damage_types:
        damages_p1 = damages_p1[damages_p1["Type"].isin(selected_damage_types)]
        damages_p2 = damages_p2[damages_p2["Type"].isin(selected_damage_types)]

    # Aggregate the data by 'Dealer' and 'Type', summing 'Damage'
    damages_p1_agg = (
        damages_p1.groupby(["Dealer", "Type"])["Damage"].sum().reset_index()
    )
    damages_p2_agg = (
        damages_p2.groupby(["Dealer", "Type"])["Damage"].sum().reset_index()
    )

    # Create the bar charts
    fig_p1 = go.Figure()
    fig_p2 = go.Figure()

    for damage_type in damage_types:
        # Filter the aggregated damages data for the current damage type
        damages_p1_type = damages_p1_agg[damages_p1_agg["Type"] == damage_type]
        damages_p2_type = damages_p2_agg[damages_p2_agg["Type"] == damage_type]

        # Add a bar to the charts for the current damage type
        fig_p1.add_trace(
            go.Bar(
                y=damages_p1_type["Dealer"],
                x=damages_p1_type["Damage"],
                orientation="h",
                marker=dict(color=damage_type_colors[damage_type]),
                name=damage_type,  # Use the damage type as the name
                showlegend=True,
            )
        )
        fig_p2.add_trace(
            go.Bar(
                y=damages_p2_type["Dealer"],
                x=damages_p2_type["Damage"],
                orientation="h",
                marker=dict(color=damage_type_colors[damage_type]),
                name=damage_type,  # Use the damage type as the name
                showlegend=True,
            )
        )

    # Set the layout for the graphs
    fig_p1.update_layout(
        title=f"Player 1 Damage Chart | Total % HP Dealt = {damages_p1['Damage'].sum()}",
        xaxis_title="% HP Damage Dealt",
        yaxis_title="Dealer",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
    )
    fig_p2.update_layout(
        title=f"Player 2 Damage Chart | Total % HP Dealt = {damages_p2['Damage'].sum()}",
        xaxis_title="% HP Damage Dealt",
        yaxis_title="Dealer",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
    )

    return fig_p1, fig_p2
