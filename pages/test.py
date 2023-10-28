import dash
from dash import html
import dash_bootstrap_components as dbc
from .navbar import navbar

dash.register_page(__name__, path="/test")


def layout():
    return dbc.Row(
        [
            dbc.Col(navbar(), width=2),
            dbc.Col(
                html.Div(
                    [
                        html.H1("This is our Test page"),
                        html.Div("This is our Test page content."),
                    ],
                ),
                width=10,
            ),
        ]
    )
