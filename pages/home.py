import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import os

from .navbar import navbar

dash.register_page(__name__, path="/")


# Get the Ninjackalytics directory so that we can randomly select pokemon from the assets/showdown_sprites directory
current_dir = os.getcwd()

# Navigate up the directory tree until we find the "Ninjackalytics" directory
while os.path.basename(current_dir) != "Ninjackalytics":
    current_dir = os.path.dirname(current_dir)


def layout():
    return html.Div(
        [
            navbar(),
            # images div
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="/assets/showdown_sprites/ninjask.gif",
                                style={"height": "25%", "width": "25%"},
                            )
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "text-align": "center",
                            "width": "14.28%",
                            "z-index": "1",
                            "position": "absolute",
                            "top": "0",
                            "left": "50%",
                            "transform": "translate(-50%, -50%)",
                        },
                    ),
                    html.Div(
                        [
                            html.Img(
                                src="/assets/showdown_sprites/ninjask.gif",
                                style={"height": "25%", "width": "25%"},
                            )
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            circle_size = "10%"
                            circle_buffer = "2%"

                            circle_divs = []
                            for i in range(1, 7):
                                circle_divs.append(
                                    html.Div(
                                        [
                                            html.Img(
                                                src="/assets/showdown_sprites/ninjask.gif",
                                                style={"height": "25%", "width": "25%"},
                                            )
                                        ],
                                        style={
                                            "display": "flex",
                                            "justify-content": "center",
                                            "text-align": "center",
                                            "width": circle_size,
                                            "z-index": "1",
                                            "position": "absolute",
                                            "top": f"{50 - (i-1)*15}%",
                                            "left": f"{50 - (i-1)*15}%",
                                            "transform": "translate(-50%, -50%)",
                                        },
                                    )
                                )

                            app.layout = html.Div(
                                [
                                    html.Div(
                                        circle_divs,
                                        style={
                                            "display": "flex",
                                            "flex": "1",
                                            "justify-content": "center",
                                            "align-items": "center",
                                            "z-index": "0",
                                            "height": "100%",
                                            "width": "100%",
                                            "position": "relative",
                                        },
                                    ),
                                    # submit button div
                                    html.Div(
                                        [
                                            html.Button("Submit Battle"),
                                            dcc.Input(
                                                placeholder="https://replay.pokemonshowdown.com/gen9ou-123",
                                                style={"flex": "1", "margin-left": "10px"},
                                            ),
                                        ],
                                        style={"display": "flex", "margin-top": "10px", "margin-bottom": "0"},
                                    ),
                                ],
                                style={"height": "100vh", "width": "100vw"},
                            )
