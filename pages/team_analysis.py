import dash
from dash import html
import dash_bootstrap_components as dbc
from .navbar import navbar

dash.register_page(__name__, path="/team_analysis")


def layout():
    return navbar()
