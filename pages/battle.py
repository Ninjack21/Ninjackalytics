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
)

# TODO
"""
- change layout so that filters apear over graphs they affect (not at top)
- add the actions breakdown graphs
- add filters for actions breadown graphs
- add the dmg/heal / entrance graphs
- add filters for dmg/heal / entrance graphs
- try to figure out how to make the mon gifs show up
"""

# TODO - ANALYZE ME
"""
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
                                battle_data["damages"]["Source_Name"].unique()
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
)
"""

# https://replay.pokemonshowdown.com/smogtours-gen9ou-725192
dash.register_page(__name__, path_template="/battle/<battle_id>")


def layout(battle_id=None):
    if battle_id:
        battle_data = parse_and_return_battle_data(battle_id)
        if not battle_data:
            return html.Div([navbar(), html.H1("Battle not found")])
        else:
            winner, loser = get_winner_loser_names(battle_data)
            fig_dmg_p1, fig_dmg_p2 = generate_damages_figures(
                battle_data=battle_data,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_turns=None,
                selected_damage_types=None,
            )
            fig_heal_p1, fig_heal_p2 = generate_healing_figures(
                battle_data=battle_data,
                selected_healing_source_names=None,
                selected_healing_receivers=None,
                selected_turns=None,
                selected_healing_types=None,
            )
            fig_hp_discrepancy = generate_hp_discrepancy_figure(
                battle_data=battle_data,
                selected_healing_source_names=None,
                selected_healing_receivers=None,
                selected_dmg_source_names=None,
                selected_dmg_dealers=None,
                selected_turns=None,
                selected_damage_types=None,
                selected_healing_types=None,
            )
            total_turns = get_total_number_of_turns(battle_data)

    else:
        winner = "Error"
        loser = "Error"
        fig_dmg_p1 = go.Figure()
        fig_dmg_p2 = go.Figure()
        fig_heal_p1 = go.Figure()
        fig_heal_p2 = go.Figure()
        fig_hp_discrepancy = go.Figure()
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
            # damage types
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
                style={"display": "inline-block", "width": "49%"},
            ),
            # damage dealer
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
                style={"display": "inline-block", "width": "49%"},
            ),
            # damage source
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
                                battle_data["damages"]["Source_Name"].unique()
                                if battle_id
                                else ["Error", "Error", "Error"]
                            )
                        ],
                        value=None,
                        multi=True,
                    ),
                ],
                style={"display": "inline-block", "width": "49%"},
            ),
            # damages chart
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_dmg_p1, id="p1-damage-chart")),
                    dbc.Col(dcc.Graph(figure=fig_dmg_p2, id="p2-damage-chart")),
                ]
            ),
            # healing types
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
                style={"display": "inline-block", "width": "49%"},
            ),
            # healing receiver
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
                style={"display": "inline-block", "width": "49%"},
            ),
            # heal source
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
                                battle_data["healing"]["Source_Name"].unique()
                                if battle_id
                                else ["Error", "Error", "Error"]
                            )
                        ],
                        value=None,
                        multi=True,
                    ),
                ],
                style={"display": "inline-block", "width": "49%"},
            ),
            # heal chart
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_heal_p1, id="p1-heal-chart")),
                    dbc.Col(dcc.Graph(figure=fig_heal_p2, id="p2-heal-chart")),
                ]
            ),
        ],
        style={"background-color": "black"},
    )


# hp discrepancy callback
@callback(
    dash.dependencies.Output("hp-disc-chart", "figure"),
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
        selected_healing_source_names=selected_healing_source_names,
        selected_healing_receivers=selected_healing_receivers,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_damage_types=selected_damage_types,
        selected_healing_types=selected_healing_types,
    )
    return hp_disc_graph


# damage graph callback
@callback(
    dash.dependencies.Output("p1-damage-chart", "figure"),
    dash.dependencies.Output("p2-damage-chart", "figure"),
    [dash.dependencies.Input("dmg-source-dropdown", "value")],
    [dash.dependencies.Input("dmg-dealer-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_dmg_source_names,
    selected_dmg_dealers,
    selected_turns,
    selected_damage_types,
    battle_id,
):
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    damages_graphs = generate_damages_figures(
        battle_data=battle_data,
        selected_dmg_source_names=selected_dmg_source_names,
        selected_dmg_dealers=selected_dmg_dealers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_damage_types=selected_damage_types,
    )
    return damages_graphs[0], damages_graphs[1]


# healing graph callback
@callback(
    dash.dependencies.Output("p1-heal-chart", "figure"),
    dash.dependencies.Output("p2-heal-chart", "figure"),
    [dash.dependencies.Input("heal-source-dropdown", "value")],
    [dash.dependencies.Input("heal-receiver-dropdown", "value")],
    [dash.dependencies.Input("turn-slider", "value")],
    [dash.dependencies.Input("heal-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(
    selected_healing_source_names,
    selected_healing_receivers,
    selected_turns,
    selected_healing_types,
    battle_id,
):
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    healing_graphs = generate_healing_figures(
        battle_data=battle_data,
        selected_healing_source_names=selected_healing_source_names,
        selected_healing_receivers=selected_healing_receivers,
        selected_turns=[t for t in range(selected_turns[0], selected_turns[1] + 1)],
        selected_healing_types=selected_healing_types,
    )
    return healing_graphs[0], healing_graphs[1]
