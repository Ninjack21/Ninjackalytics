from flask import session
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import plotly.graph_objects as go
import plotly.colors as pcolors
from .navbar import navbar
from .page_utilities.general_utility import (
    find_closest_sprite,
    DatabaseData,
    FormatData,
    WinrateCalculator,
)
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
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


def display_top_threats(
    team1=None,
    team2=None,
    fmat=None,
    p1_name=None,
    p2_name=None,
    engine_name="antimeta",
):
    db = DatabaseData(fmat)
    fdata = FormatData(fmat, db)
    winrate_calculator = WinrateCalculator(fdata, engine_name)

    if team1 is None or team2 is None or fmat is None:
        return html.Div("")
    else:
        winrates1 = winrate_calculator.get_team_winrate_against_other_team(team1, team2)
        winrates2 = winrate_calculator.get_team_winrate_against_other_team(team2, team1)

        norm1 = winrate_calculator.normalized_winrate(winrates1, team2)
        norm2 = winrate_calculator.normalized_winrate(winrates2, team1)

        team1_avg_norm_wr = (norm1 + (100 - norm2)) / 2

        # WR calc returns the expected winrates against each mon on the opposing team (index) so have to
        # reverse here to see the expected winrates for the originally passed in team (which shows up as the idx
        # of the opposite calculated wrs. I know that's confusing)
        team1_wr = winrates2.copy()
        team2_wr = winrates1.copy()

        team1_wr["winrate"] = 100 - team1_wr["winrate"]
        team2_wr["winrate"] = 100 - team2_wr["winrate"]

        team1_wr = team1_wr.sort_values("winrate", ascending=False)
        team2_wr = team2_wr.sort_values("winrate", ascending=False)

        chosen_palette = pcolors.sequential.ice

        global_min_wr = min(team1_wr["winrate"].min(), team2_wr["winrate"].min())
        global_max_wr = max(team1_wr["winrate"].max(), team2_wr["winrate"].max())

        # Function to map winrate to color with a smooth transition from 0 to 100
        def map_winrate_to_color(winrate, chosen_palette=chosen_palette):
            # Normalize the winrate to the range [0, 1]
            normalized = winrate / 100
            # Calculate the color index based on the normalized winrate
            color_index = int(normalized * (len(chosen_palette) - 1))
            # Ensure the color index is within the bounds of the palette
            color_index = max(0, min(color_index, len(chosen_palette) - 1))
            return chosen_palette[color_index]

        # Apply color mapping
        colors1 = team1_wr["winrate"].apply(map_winrate_to_color)
        colors2 = team2_wr["winrate"].apply(map_winrate_to_color)

        fig1 = go.Figure()
        fig1.add_trace(
            go.Bar(
                x=team1_wr.index,
                y=team1_wr["winrate"],
                marker_color=colors1,
            )
        )

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=team2_wr.index,
                y=team2_wr["winrate"],
                marker_color=colors2,
            )
        )

        fig1.update_layout(
            template="plotly_dark",
            title=f"{p1_name}'s Threats Defined by Expected Winrate<br>against Enemy Team"
            + "<br>Pure White = 100% WR Expectation, Darker Blues = Lower WR Expectation",
        )
        fig2.update_layout(
            template="plotly_dark",
            title=f"{p2_name}'s Threats Defined by Expected Winrate<br>against Enemy Team"
            + "<br>Pure White = 100% WR Expectation, Darker Blues = Lower WR Expectation",
        )

        expected_winrate_text = (
            f"Expected likelihood of {p1_name} winning: {team1_avg_norm_wr:.2f}%"
        )

        return html.Div(
            [
                html.H3(expected_winrate_text, style={"textAlign": "center"}),
                html.Div(
                    [
                        dcc.Graph(
                            figure=fig1,
                            style={
                                "width": "49%",
                                "display": "inline-block",
                                "padding": "20px",
                            },
                        ),
                        dcc.Graph(
                            figure=fig2,
                            style={
                                "width": "49%",
                                "display": "inline-block",
                                "padding": "20px",
                            },
                        ),
                    ],
                    style={"display": "flex", "justify-content": "space-around"},
                ),
            ]
        )


def display_mid_battle_analysis():
    return html.Div("This is the mid-battle analysis content")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
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
                id="loading-team-preview-content",
                children=[
                    # Placeholder for dynamic content. This Div will be updated via callbacks.
                    html.Div(id="dynamic-content-pre-battle-analysis")
                ],
                fullscreen=False,  # Set True for fullscreen loading, if needed
            ),
            dcc.Loading(
                id="loading-mid-battle-content",
                children=[
                    # Placeholder for dynamic content. This Div will be updated via callbacks.
                    html.Div(id="dynamic-content-mid-battle-analysis")
                ],
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
            "min-height": "100vh",
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

    return [
        html.Div(
            [
                display_teams_with_sprites(team1, team2, p1_name, p2_name),
                display_top_threats(team1, team2, fmat, p1_name, p2_name),
            ]
        )
    ]
