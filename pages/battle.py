import dash
from dash import html, dcc, callback
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from .navbar import navbar
from .battle_funcs import (
    parse_and_return_battle_data,
    generate_damages_figures,
    generate_healing_figures,
    get_winner_loser_names,
    generate_hp_discrepancy_figure,
    get_total_number_of_turns,
    generate_action_choices_pie_chart,
    get_winner_pnum,
    generate_damage_per_entrance_figures,
    generate_heal_per_entrance_figures,
    generate_hp_taken_figures,
    get_team_sprites,
)


# TODO
"""
- try to figure out how to make the mon gifs show up
"""


# https://replay.pokemonshowdown.com/smogtours-gen9ou-725192
dash.register_page(__name__, path_template="/battle/<battle_id>")

sprite_h_px = "100px"
sprite_w_px = "75px"


def layout(battle_id=None):
    if battle_id:
        battle_data = parse_and_return_battle_data(battle_id)
        if not battle_data:
            return html.Div([navbar(), html.H1("Battle not found")])
        else:
            winner_pnum = get_winner_pnum(battle_data)
            winner, loser = get_winner_loser_names(battle_data)
            fig_dmg_winner, fig_dmg_loser = generate_damages_figures(
                battle_data=battle_data,
                selected_winner_actions=None,
                selected_loser_actions=None,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_turns=None,
                selected_damage_types=None,
            )
            fig_heal_winner, fig_heal_loser = generate_healing_figures(
                battle_data=battle_data,
                selected_winner_actions=None,
                selected_loser_actions=None,
                selected_healing_source_names=None,
                selected_healing_receivers=None,
                selected_turns=None,
                selected_healing_types=None,
            )
            fig_hp_discrepancy = generate_hp_discrepancy_figure(
                battle_data=battle_data,
                selected_winner_actions=None,
                selected_loser_actions=None,
                selected_healing_source_names=None,
                selected_healing_receivers=None,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_turns=None,
                selected_damage_types=None,
                selected_healing_types=None,
            )
            fig_actions_winner, fig_actions_loser = generate_action_choices_pie_chart(
                battle_data=battle_data,
                selected_turns=None,
                selected_winner_actions=None,
                selected_loser_actions=None,
            )
            (
                fig_dmg_per_entrance_winner,
                fig_dmg_per_entrance_loser,
            ) = generate_damage_per_entrance_figures(
                battle_data=battle_data,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_dmg_types=None,
            )
            (
                fig_heal_per_entrance_winner,
                fig_heal_per_entrance_loser,
            ) = generate_heal_per_entrance_figures(
                battle_data=battle_data,
                selected_heal_source_names=None,
                selected_heal_receivers=None,
                selected_heal_types=None,
            )
            (
                fig_hp_taken_winner,
                fig_hp_taken_loser,
            ) = generate_hp_taken_figures(
                battle_data=battle_data,
                selected_winner_actions=None,
                selected_loser_actions=None,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_turns=None,
                selected_dmg_types=None,
            )
            winner_team_sprites, loser_team_sprites = get_team_sprites(battle_data)

            total_turns = get_total_number_of_turns(battle_data)

    else:
        winner = "Error"
        loser = "Error"
        fig_dmg_winner = go.Figure()
        fig_dmg_loser = go.Figure()
        fig_heal_winner = go.Figure()
        fig_heal_loser = go.Figure()
        fig_hp_discrepancy = go.Figure()
        fig_actions_winner = go.Figure()
        fig_actions_loser = go.Figure()
        fig_dmg_per_entrance_winner = go.Figure()
        fig_dmg_per_entrance_loser = go.Figure()
        fig_heal_per_entrance_winner = go.Figure()
        fig_heal_per_entrance_loser = go.Figure()
        fig_hp_taken_winner = go.Figure()
        fig_hp_taken_loser = go.Figure()
        total_turns = 1

    return html.Div(
        [
            navbar(),
            # hidden div to store bid
            html.Div(id="battle-id", children=battle_id, style={"display": "none"}),
            # hp discrepancy chart
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_hp_discrepancy, id="hp-disc-chart")),
                ]
            ),
            # turn slicer
            html.Div(
                [
                    html.H3(
                        "Turns Slicer",
                        style={
                            "text-align": "center",
                            "color": "white",
                            "background-color": "#343a40",
                            "padding": "10px",
                        },
                    ),
                    dcc.RangeSlider(
                        id="turn-slider",
                        min=0,
                        max=total_turns,
                        value=[0, total_turns],
                        marks={
                            str(turn): str(turn) for turn in range(1, total_turns + 1)
                        },
                        step=None,
                    ),
                ],
                style={"display": "inline-block", "width": "100%"},
            ),
            # team sprites
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=sprite,
                                        style={
                                            "height": sprite_h_px,
                                            "width": sprite_w_px,
                                            "margin": "5px",
                                        },
                                    )
                                    for name, sprite in winner_team_sprites.items()
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "flex-start",
                                },
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=sprite,
                                        style={
                                            "height": sprite_h_px,
                                            "width": sprite_w_px,
                                            "margin": "5px",
                                        },
                                    )
                                    for name, sprite in loser_team_sprites.items()
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "flex-end",
                                },
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            # dmg taken chart
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_hp_taken_winner, id="winner-damage-taken-chart"
                        )
                    ),
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_hp_taken_loser, id="loser-damage-taken-chart"
                        )
                    ),
                ]
            ),
            # damage filters
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Damage Types",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="damage-type-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["damages"]["Type"].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Damage Dealers",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="dmg-dealer-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["damages"]["Dealer"].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Damage Source Names",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="dmg-source-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["damages"][
                                                "Source_Name"
                                            ].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                ]
            ),
            # damages chart
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_dmg_winner, id="winner-damage-chart")),
                    dbc.Col(dcc.Graph(figure=fig_dmg_loser, id="loser-damage-chart")),
                ]
            ),
            # dmg/entrance chart
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_dmg_per_entrance_winner,
                            id="winner-dmg-per-entrance-chart",
                        )
                    ),
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_dmg_per_entrance_loser,
                            id="loser-dmg-per-entrance-chart",
                        )
                    ),
                ]
            ),
            # healing filters
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Healing Types",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="heal-type-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["healing"]["Type"].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Healing Receivers",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="heal-receiver-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["healing"]["Receiver"].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Healing Source Names",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="heal-source-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["healing"][
                                                "Source_Name"
                                            ].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                ]
            ),
            # heal chart
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_heal_winner, id="winner-heal-chart")),
                    dbc.Col(dcc.Graph(figure=fig_heal_loser, id="loser-heal-chart")),
                ]
            ),
            # heal/entrance chart
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_heal_per_entrance_winner,
                            id="winner-heal-per-entrance-chart",
                        )
                    ),
                    dbc.Col(
                        dcc.Graph(
                            figure=fig_heal_per_entrance_loser,
                            id="loser-heal-per-entrance-chart",
                        )
                    ),
                ]
            ),
            # actions filters
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    f"{winner} Actions",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="winner-action-type-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["actions"]["Action"][
                                                battle_data["actions"]["Player_Number"]
                                                == winner_pnum
                                            ].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    f"{loser} Actions",
                                    style={
                                        "text-align": "center",
                                        "color": "white",
                                        "background-color": "#343a40",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="loser-action-type-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in (
                                            battle_data["actions"]["Action"][
                                                battle_data["actions"]["Player_Number"]
                                                == (1 if winner_pnum == 2 else 2)
                                            ].unique()
                                            if battle_id
                                            else ["Error", "Error", "Error"]
                                        )
                                    ],
                                    value=None,
                                    multi=True,
                                ),
                            ],
                            style={"display": "inline-block", "width": "100%"},
                        ),
                        width=4,
                    ),
                ]
            ),
            # actions chart
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(figure=fig_actions_winner, id="winner-actions-chart")
                    ),
                    dbc.Col(
                        dcc.Graph(figure=fig_actions_loser, id="loser-actions-chart")
                    ),
                ]
            ),
        ],
        style={"background-color": "black"},
    )


# hp discrepancy callback
@callback(
    dash.dependencies.Output("hp-disc-chart", "figure"),
    [dash.dependencies.Input("winner-action-type-dropdown", "value")],
    [dash.dependencies.Input("loser-action-type-dropdown", "value")],
    [dash.dependencies.Input("heal-source-dropdown", "value")],
    [dash.dependencies.Input("heal-receiver-dropdown", "value")],
    [dash.dependencies.Input("dmg-source-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("dmg-dealer-dropdown", "value")],
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.Input("heal-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_winner_actions,
    selected_loser_actions,
    selected_healing_source_names,
    selected_healing_receivers,
    selected_dmg_source_names,
    selected_turns,
    selected_dmg_dealers,
    selected_damage_types,
    selected_healing_types,
    battle_id,
):
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    hp_disc_graph = generate_hp_discrepancy_figure(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_healing_source_names=selected_healing_source_names,
        selected_healing_receivers=selected_healing_receivers,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_damage_types=selected_damage_types,
        selected_healing_types=selected_healing_types,
    )
    return hp_disc_graph


# damage taken graph callback
@callback(
    dash.dependencies.Output("winner-damage-taken-chart", "figure"),
    dash.dependencies.Output("loser-damage-taken-chart", "figure"),
    [dash.dependencies.Input("winner-action-type-dropdown", "value")],
    [dash.dependencies.Input("loser-action-type-dropdown", "value")],
    [dash.dependencies.Input("dmg-source-dropdown", "value")],
    [dash.dependencies.Input("dmg-dealer-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_winner_actions,
    selected_loser_actions,
    selected_dmg_source_names,
    selected_dmg_dealers,
    selected_turns,
    selected_dmg_types,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    dmgs_taken_graphs = generate_hp_taken_figures(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_dmg_types=selected_dmg_types,
    )
    return dmgs_taken_graphs[0], dmgs_taken_graphs[1]


# damage graph callback
@callback(
    dash.dependencies.Output("winner-damage-chart", "figure"),
    dash.dependencies.Output("loser-damage-chart", "figure"),
    [dash.dependencies.Input("winner-action-type-dropdown", "value")],
    [dash.dependencies.Input("loser-action-type-dropdown", "value")],
    [dash.dependencies.Input("dmg-source-dropdown", "value")],
    [dash.dependencies.Input("dmg-dealer-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_winner_actions,
    selected_loser_actions,
    selected_dmg_source_names,
    selected_dmg_dealers,
    selected_turns,
    selected_damage_types,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    damages_graphs = generate_damages_figures(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_damage_types=selected_damage_types,
    )
    return damages_graphs[0], damages_graphs[1]


# dmg/entrance graph callback
@callback(
    dash.dependencies.Output("winner-dmg-per-entrance-chart", "figure"),
    dash.dependencies.Output("loser-dmg-per-entrance-chart", "figure"),
    [dash.dependencies.Input("dmg-source-dropdown", "value")],
    [dash.dependencies.Input("dmg-dealer-dropdown", "value")],
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_dmg_source_names,
    selected_dmg_dealers,
    selected_damage_types,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    dmg_per_entrance_graphs = generate_damage_per_entrance_figures(
        battle_data=battle_data,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_dmg_types=selected_damage_types,
    )
    return dmg_per_entrance_graphs[0], dmg_per_entrance_graphs[1]


# healing graph callback
@callback(
    dash.dependencies.Output("winner-heal-chart", "figure"),
    dash.dependencies.Output("loser-heal-chart", "figure"),
    [dash.dependencies.Input("winner-action-type-dropdown", "value")],
    [dash.dependencies.Input("loser-action-type-dropdown", "value")],
    [dash.dependencies.Input("heal-source-dropdown", "value")],
    [dash.dependencies.Input("heal-receiver-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("heal-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_winner_actions,
    selected_loser_actions,
    selected_healing_source_names,
    selected_healing_receivers,
    selected_turns,
    selected_healing_types,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    healing_graphs = generate_healing_figures(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_healing_source_names=selected_healing_source_names,
        selected_healing_receivers=selected_healing_receivers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_healing_types=selected_healing_types,
    )
    return healing_graphs[0], healing_graphs[1]


# heal/entrance graph callback
@callback(
    dash.dependencies.Output("winner-heal-per-entrance-chart", "figure"),
    dash.dependencies.Output("loser-heal-per-entrance-chart", "figure"),
    [dash.dependencies.Input("heal-source-dropdown", "value")],
    [dash.dependencies.Input("heal-receiver-dropdown", "value")],
    [dash.dependencies.Input("heal-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_heal_source_names,
    selected_heal_receivers,
    selected_heal_types,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    healing_per_entrance_graphs = generate_heal_per_entrance_figures(
        battle_data=battle_data,
        selected_heal_source_names=selected_heal_source_names,
        selected_heal_receivers=selected_heal_receivers,
        selected_heal_types=selected_heal_types,
    )
    return healing_per_entrance_graphs[0], healing_per_entrance_graphs[1]


# actions graph callback
@callback(
    dash.dependencies.Output("winner-actions-chart", "figure"),
    dash.dependencies.Output("loser-actions-chart", "figure"),
    [dash.dependencies.Input("winner-action-type-dropdown", "value")],
    [dash.dependencies.Input("loser-action-type-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_winner_actions,
    selected_loser_actions,
    selected_turns,
    battle_id,
):
    # Check if the components exist yet - to get around initial layout not defined error
    if not dash.callback_context.triggered:
        return dash.no_update, dash.no_update
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    damages_graphs = generate_action_choices_pie_chart(
        battle_data=battle_data,
        selected_winner_actions=selected_winner_actions,
        selected_loser_actions=selected_loser_actions,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
    )
    return damages_graphs[0], damages_graphs[1]
