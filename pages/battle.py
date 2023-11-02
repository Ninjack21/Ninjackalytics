import dash
from dash import html, dcc, callback
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from ninjackalytics.services.battle_parsing import BattleParser, Battle, BattlePokemon
from .navbar import navbar
from .battle_funcs import parse_and_return_battle_data, generate_damages_figures

# https://replay.pokemonshowdown.com/smogtours-gen9ou-725192
dash.register_page(__name__, path_template="/battle/<battle_id>")


def layout(battle_id=None):
    if battle_id:
        battle_data = parse_and_return_battle_data(battle_id)
        if not battle_data:
            return html.Div([navbar(), html.H1("Battle not found")])
        else:
            fig_dmg_p1, fig_dmg_p2 = generate_damages_figures(battle_data, None)
    else:
        fig_dmg_p1 = go.Figure()
        fig_dmg_p2 = go.Figure()

    return html.Div(
        [
            navbar(),
            html.Div(
                id="battle-id", children=battle_id, style={"display": "none"}
            ),  # hidden div to store bid
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
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_dmg_p1, id="p1-damage-chart")),
                    dbc.Col(dcc.Graph(figure=fig_dmg_p2, id="p2-damage-chart")),
                ]
            ),
        ],
        style={"background-color": "black"},
    )


@callback(
    dash.dependencies.Output("p1-damage-chart", "figure"),
    dash.dependencies.Output("p2-damage-chart", "figure"),
    [dash.dependencies.Input("damage-type-dropdown", "value")],
    [dash.dependencies.State("battle-id", "children")],
)
def update_output(selected_damage_types, battle_id):
    battle_data = parse_and_return_battle_data(
        battle_id
    )  # You will need to provide the battle_id here
    damages_graphs = generate_damages_figures(battle_data, selected_damage_types)
    return damages_graphs[0], damages_graphs[1]
