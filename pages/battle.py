import dash
from dash import html
import dash_bootstrap_components as dbc
from ninjackalytics.services.database_interactors.battle_data_retriever import (
    BattleDataRetriever,
)
from .navbar import navbar

dash.register_page(__name__, path_template="/battle/<battle_id>")

battle_retriever = BattleDataRetriever()


def layout(battle_id=None):
    return html.Div([navbar(), html.H1(f"battle page: {battle_id}")])
