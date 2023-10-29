import dash
from dash import html
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

battle_retriever = BattleDataRetriever()


def layout(battle_id=None):
    if battle_id:
        exists = battle_retriever.check_if_battle_exists(battle_id)
        return html.Div([navbar(), html.H1(f"Battle Exists = {exists}")])
    else:
        return html.Div([navbar(), html.H1("No battle id provided")])
