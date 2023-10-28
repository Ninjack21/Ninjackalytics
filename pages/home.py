import dash
from dash import html
import dash_bootstrap_components as dbc
from .navbar import navbar

dash.register_page(__name__, path="/")


def layout():
    return navbar()
