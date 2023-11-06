import dash
from dash import html
import dash_bootstrap_components as dbc
from .navbar import navbar

dash.register_page(__name__, path="/page_registry")


def layout():
    return html.Div([navbar(), html.P(f"{dash.page_registry['pages.battle']}")])
