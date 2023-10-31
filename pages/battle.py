import dash
from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from ninjackalytics.services.database_interactors import (
    BattleDataRetriever,
    BattleDataUploader,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from .navbar import navbar

dash.register_page(__name__, path_template="/battle/<battle_id>")

# TODO NOTE TODO: UPDATE THIS TO BE PRODUCTION IN MAIN BRANCH
import os

os.environ["FLASK_ENV"] = "testing"

retriever = BattleDataRetriever()


def layout(battle_id=None):
    if battle_id:
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
                print(e)
                return html.Div([navbar(), html.H1("Error parsing battle")])
        battle_data = retriever.get_battle_data(battle_id)
        damages = battle_data["damages"]

        # Filter the damages data for each player
        damages_p1 = damages[damages["Receiver_Player_Number"] == 2]
        damages_p2 = damages[damages["Receiver_Player_Number"] == 1]

        # Create the bar charts
        fig_p1 = go.Figure(
            data=[
                go.Bar(
                    y=damages_p1["Dealer"],
                    x=damages_p1["Damage"],
                    orientation="h",
                    marker=dict(
                        color=damages_p1["Damage"],
                        colorscale="Viridis",
                        colorbar=dict(title="% HP Dealt"),
                    ),
                )
            ]
        )
        fig_p2 = go.Figure(
            data=[
                go.Bar(
                    y=damages_p2["Dealer"],
                    x=damages_p2["Damage"],
                    orientation="h",
                    marker=dict(
                        color=damages_p2["Damage"],
                        colorscale="Viridis",
                        colorbar=dict(title="Total Damage"),
                    ),
                )
            ]
        )

        # Set the layout for the graphs
        fig_p1.update_layout(
            title="Player 1 Damage Chart",
            xaxis_title="% HP Damage Dealt",
            yaxis_title="Dealer",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white"),
        )
        fig_p2.update_layout(
            title="Player 2 Damage Chart",
            xaxis_title="% HP Damage Dealt",
            yaxis_title="Dealer",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white"),
        )

        return html.Div(
            [
                navbar(),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(figure=fig_p1, id="p1-damage-chart")),
                        dbc.Col(dcc.Graph(figure=fig_p2, id="p2-damage-chart")),
                    ]
                ),
            ],
            style={"background-color": "black"},
        )
    else:
        return html.Div([navbar(), html.H1("No battle id provided")])
