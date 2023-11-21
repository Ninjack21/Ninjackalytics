import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import random
from .navbar import navbar
from .general_utility import get_random_sprite

dash.register_page(__name__, path="/")

sprite_height = "70%"
sprite_width = "70%"

import os

current_dir = os.path.dirname(__file__)
while current_dir != "/":
    if os.path.basename(current_dir) == "Ninjackalytics":
        break
    current_dir = os.path.dirname(current_dir)

sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
sprites = os.listdir(sprite_dir)


def layout():
    def submit_battle():
        input_value = dcc.Input(
            id="input-url",
            placeholder="https://replay.pokemonshowdown.com/gen9ou-123",
            type="text",
            value="",
        ).value
        if input_value:
            parsed_battle_id = input_value.split(".com/")[1]
            return dcc.Location(
                pathname=f"/battle/{parsed_battle_id}", id="battle-page"
            )
        else:
            return html.Div("Please enter a valid URL")

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
                            "align-items": "center",
                            "text-align": "center",
                            "width": "50%",
                            "z-index": "1",
                            "margin-top": "20vh",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        src=get_random_sprite(),
                                        style={
                                            "height": sprite_height,
                                            "width": sprite_width,
                                        },
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "text-align": "center",
                                    "width": "33.33%",
                                    "z-index": "1",
                                    "margin-top": "10px",
                                    "margin-bottom": "10px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flex-wrap": "wrap",
                            "justify-content": "center",
                            "align-items": "center",
                            "z-index": "1",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flex": "1",
                    "justify-content": "center",
                    "align-items": "center",
                    "z-index": "1",
                },
            ),
            html.Div(
                [
                    dbc.Button(
                        "Submit Battle",
                        id="submit-button",
                        n_clicks=0,
                        style={"background-color": "#333", "color": "white"},
                    ),
                    dcc.Input(
                        id="input-url",
                        placeholder="https://replay.pokemonshowdown.com/gen9ou-123",
                        type="text",
                        value="",
                        style={"width": "100%"},
                    ),
                    html.Div(id="output-div"),
                ],
                style={
                    "width": "50%",
                    "margin-top": "10px",
                    "margin-bottom": "0",
                    "position": "fixed",
                    "bottom": "20px",
                    "left": "20px",
                },
            ),
            dcc.Location(id="url", refresh=False),
        ],
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
        },
    )


@callback(
    dash.dependencies.Output("output-div", "children"),
    [dash.dependencies.Input("submit-button", "n_clicks")],
    [dash.dependencies.State("input-url", "value")],
)
def update_output(n_clicks, input_value):
    if n_clicks > 0:
        if input_value:
            parsed_battle_id = input_value.split(".com/")[1]
            return dcc.Location(href=f"battle/{parsed_battle_id}", id="Battle")
        else:
            return html.Div("Please enter a valid URL")
