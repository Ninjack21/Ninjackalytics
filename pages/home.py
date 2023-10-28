import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .navbar import navbar

dash.register_page(__name__, path="/")


def layout():
    return html.Div(
        [
            navbar(),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="/assets/Ninjack.png",
                                style={"height": "50%", "width": "50%"},
                            )
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "text-align": "center",
                            "width": "50%",
                        },
                    ),
                    html.Div(
                        [
                            html.Img(
                                src="/assets/Ninjack.png",
                                style={"height": "50%", "width": "50%"},
                            )
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "text-align": "center",
                            "width": "50%",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flex": "1",
                    "justify-content": "center",
                    "align-items": "center",
                },
            ),
            html.Div(
                [
                    html.Button("Submit Battle"),
                    dcc.Input(
                        placeholder="https://replay.pokemonshowdown.com/gen9ou-123",
                        style={"flex": "1", "margin-left": "10px"},
                    ),
                ],
                style={"display": "flex", "margin-top": "10px"},
            ),
        ],
        style={"display": "flex", "flex-direction": "column", "flex": "1"},
    )
