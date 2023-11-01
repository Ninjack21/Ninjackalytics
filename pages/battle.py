import dash
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from ninjackalytics.services.database_interactors import (
    BattleDataRetriever,
    BattleDataUploader,
)
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from .navbar import navbar
from .battle_funcs import parse_and_return_battle_data, generate_damages_figures

# https://replay.pokemonshowdown.com/smogtours-gen9ou-725192
dash.register_page(__name__, path_template="/battle/<battle_id>")

# TODO NOTE TODO: UPDATE THIS TO BE PRODUCTION IN MAIN BRANCH
import os

os.environ["FLASK_ENV"] = "testing"

retriever = BattleDataRetriever()


def layout(battle_id=None):
    if battle_id:
        battle_data = parse_and_return_battle_data(battle_id)
        if not battle_data:
            return html.Div([navbar(), html.H1("Battle not found")])
        else:
            damages_graphs = generate_damages_figures(battle_data)

            return html.Div(
                [navbar(), damages_graphs],
                style={"background-color": "black"},
            )
    else:
        return html.Div([navbar(), html.H1("No battle id provided")])
