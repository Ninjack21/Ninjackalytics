import pandas as pd
from datetime import datetime
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from .navbar import navbar
from .page_utilities.general_utility import (
    find_closest_sprite,
    DatabaseData,
    FormatData,
    WinrateCalculator,
)

dash.register_page(__name__, path="/pre_battle_analysis")


def pre_battle_text_component():
    return html.Div(
        [
            dcc.Textarea(
                id="battle-input",
                value="",  # Initial value can be empty or some placeholder text
                style={"width": "100%", "height": 200},  # Customize the size as needed
                placeholder="""Format:
[Gen 9] OU
Rated battle
Species Clause: Limit one of each Pokémon
OHKO Clause: OHKO moves are banned
Evasion Items Clause: Evasion items are banned
Evasion Moves Clause: Evasion moves are banned
Endless Battle Clause: Forcing endless battles is banned
HP Percentage Mod: HP is shown in percentages
Sleep Moves Clause: Sleep-inducing moves are banned
Player1's team:
Iron Valiant / Ogerpon-Cornerstone / Skeledirge / Corviknight / Raging Bolt / Ting-Lu
Player2's team:
Samurott-Hisui / Volcarona / Iron Valiant / Roaring Moon / Kingambit / Deoxys-Speed""",
            ),
            html.Button("Submit", id="submit-val", n_clicks=0),
            html.Div(id="output"),
        ]
    )


def display_teams_with_sprites(team1=None, team2=None, p1_name=None, p2_name=None):
    if team1 is None or team2 is None:
        return html.Div("")
    else:
        p1_name = p1_name if p1_name else "Player 1"
        p2_name = p2_name if p2_name else "Player 2"
        return html.Div(
            [
                html.Div(
                    [
                        html.H3(f"{p1_name}'s Team", style={"text-align": "center"}),
                        html.Div(
                            [
                                html.Div(  # This Div groups the image and the name together
                                    [
                                        html.Img(
                                            src=find_closest_sprite(mon),
                                            style={
                                                "width": "50px",
                                                "height": "50px",
                                            },
                                        ),
                                        html.Div(
                                            mon, style={"text-align": "center"}
                                        ),  # Pokémon name below the image
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "margin": "10px",
                                    },  # Add some spacing around each group
                                )
                                for mon in team1
                            ],
                            style={"text-align": "center"},
                        ),
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
                html.Div(
                    [
                        html.H3(f"{p2_name}'s Team", style={"text-align": "center"}),
                        html.Div(
                            [
                                html.Div(  # This Div groups the image and the name together
                                    [
                                        html.Img(
                                            src=find_closest_sprite(mon),
                                            style={
                                                "width": "50px",
                                                "height": "50px",
                                            },
                                        ),
                                        html.Div(
                                            mon, style={"text-align": "center"}
                                        ),  # Pokémon name below the image
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "margin": "10px",
                                    },  # Add some spacing around each group
                                )
                                for mon in team2
                            ],
                            style={"text-align": "center"},
                        ),
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
            ],
            style={
                "width": "100%",
                "display": "flex",
                "justify-content": "center",
            },
        )


def layout():
    return html.Div(
        [
            navbar(),
            dcc.Store("format-store"),
            dcc.Store("submit-trigger", data={"count-clicks": 0}),
            html.H1("Pre Battle Analysis"),
            html.Div(
                [
                    html.H2("Enter the Team Preview Text"),
                    pre_battle_text_component(),
                ],
                style={"width": "50%", "margin": "auto"},
            ),
            dcc.Loading(
                id="loading-dynamic-content",
                children=[
                    # Placeholder for dynamic content. This Div will be updated via callbacks.
                    html.Div(id="dynamic-content-pre-battle-analysis")
                ],
                type="circle",  # Choose the spinner style
                color="#FFFFFF",  # Customize the spinner color
                fullscreen=False,  # Set True for fullscreen loading, if needed
            ),
            dcc.ConfirmDialog(
                id="format-error-dialog",
                message="The format could not be determined from the provided text. Remove all text and look at the placeholder text to see what is expected.",
            ),
        ],
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
            "color": "white",
        },
    )


@callback(
    [
        Output("format-store", "data"),
        Output("format-error-dialog", "displayed"),
        Output("submit-trigger", "data"),
    ],
    [Input("submit-val", "n_clicks")],
    [State("battle-input", "value"), State("submit-trigger", "data")],
)
def update_format_data_store(n_clicks, battle_input, submit_data):
    if n_clicks > 0:
        if n_clicks > submit_data["count-clicks"] and len(battle_input) > 0:
            try:
                # Attempt to extract the format from the input
                fmat = battle_input.split("Format:\n")[1].split("\n")[0]
                # Update the submission ID to mark this submission as processed
                return fmat, False, {"count-clicks": n_clicks}
            except IndexError:
                # Format extraction failed; trigger the error dialog
                return no_update, True, {"count-clicks": n_clicks}

    # If no clicks detected or to reset for a new action, update without changing the count-clicks
    return no_update, False, submit_data if submit_data else {"count-clicks": n_clicks}


@callback(
    [
        Output("dynamic-content-pre-battle-analysis", "children"),
    ],
    [Input("format-store", "data")],
    [State("battle-input", "value")],
)
def update_dynamic_content(fmat, battle_input):
    team1_text = battle_input.split("'s team:\n")[1].split("\n")[0]
    team2_text = battle_input.split("'s team:\n")[2].split("\n")[0]
    team1 = team1_text.split(" / ")
    team2 = team2_text.split(" / ")

    p1_name = battle_input.split("'s team:\n")[0].split("\n")[-1]
    p2_name = battle_input.split("'s team:\n")[1].split("\n")[-1]

    return [display_teams_with_sprites(team1, team2, p1_name, p2_name)]
