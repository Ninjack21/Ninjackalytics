import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import random
from .navbar import navbar

dash.register_page(__name__, path="/")

sprite_height = "80%"
sprite_width = "80%"

import os

current_dir = os.path.dirname(__file__)
while current_dir != "/":
    if os.path.basename(current_dir) == "Ninjackalytics":
        break
    current_dir = os.path.dirname(current_dir)

sprite_dir = os.path.join(current_dir, "assets/showdown_sprites")
sprites = os.listdir(sprite_dir)


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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                                        src=os.path.join(
                                            sprite_dir, random.choice(sprites)
                                        ).split("Ninjackalytics")[-1],
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
                        style={"background-color": "#333", "color": "white"},
                    ),
                    dbc.Input(
                        placeholder="https://replay.pokemonshowdown.com/gen9ou-123",
                    ),
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
        ],
        style={
            "background-image": "url('/assets/background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
        },
    )
