import dash
from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from .navbar import navbar
from .general_utility import find_closest_sprite
from .team_analysis_funcs import (
    get_viable_pokemon,
)
from .team_classes import DatabaseData, FormatData, TeamSolver, DisplayTeam

dash.register_page(__name__, path="/team_analysis")

mon_height = "85px"
mon_width = "85px"


def layout():
    db_data = DatabaseData()
    viable_formats = (
        db_data.viable_formats
    )  # have to do this upon init to avoid hard coding options
    format_data = FormatData(
        battle_format=viable_formats[0],
        db=db_data,
    )
    format_mons = format_data.get_format_available_mons()

    return html.Div(
        [
            navbar(),
            # ===== STORES =====
            dcc.Store(
                id="viable-pokemon-store",
                data=[format_mons],
            ),
            html.H1("Team Builder Tool"),
            html.Br(),
            html.Label("Format", style={"color": "white"}),
            dcc.Dropdown(
                id="format-selector",
                options=viable_formats,
                value=viable_formats[0],
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
            # ===== POKEMON SELECTIONS ======
            html.Label("Pokemon Selections", style={"color": "white"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id=f"pokemon-selector-{i}",
                                options=[
                                    {"label": pokemon_name, "value": pokemon_name}
                                    for pokemon_name in get_viable_pokemon(
                                        format_pokemon=format_mons,
                                        selected_ignore_mons=[],
                                        already_used_mons=[],
                                    )
                                ],
                                value=None,
                                placeholder="fill for me",
                                style={
                                    "width": "250px",
                                    "color": "black",
                                    "background-color": "white",
                                },
                            ),
                            html.Img(
                                id=f"pokemon-sprite-{i}",
                                src=None,
                                style={
                                    "height": mon_height,
                                    "width": mon_width,
                                    "padding-top": "10px",
                                    "padding-left": "10px",  # Add padding to the left
                                },
                            ),
                        ],
                        width=2,
                    )
                    for i in range(6)
                ]
            ),
            html.Br(),
            # ===== DON'T USE POKEMON ======
            html.Label("Don't Use Pokemon", style={"color": "white"}),
            dcc.Dropdown(
                id="dont-use-pokemon-selector",
                options=[
                    {"label": pokemon_name, "value": pokemon_name}
                    for pokemon_name in get_viable_pokemon(
                        format_pokemon=format_mons,
                        selected_ignore_mons=[],
                        already_used_mons=[],
                    )
                ],
                multi=True,
                placeholder="Select Pokemon",
                style={
                    "width": "375px",
                    "color": "black",
                    "background-color": "white",
                },
            ),
            html.Br(),
            # ===== BUILD TEAM OPTIONS ======
            html.Label("Creativity", style={"color": "white"}),
            dcc.Input(
                id="creativity-input",
                type="number",
                min=0,
                max=100,
                step=1,
                value=50,
                style={
                    "width": "100px",
                    "color": "black",
                    "background-color": "white",
                    "margin-bottom": "10px",
                },
            ),
            html.Br(),
            html.Div(
                [
                    dbc.Button(
                        "Build Team",
                        id="build-team-button",
                        n_clicks=0,
                        color="primary",
                        className="mr-1",
                    ),
                ]
            ),
            # ========= BUILT TEAM FIELDS =========
            html.Label("Completed Team", style={"color": "white"}),
            dcc.Loading(
                id="loading",
                type="circle",
                children=[
                    # suggested team and sprites
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dcc.Input(
                                        id=f"team-mon-{i}",
                                        type="text",
                                        value=None,
                                        placeholder="Click Build Team!",
                                        disabled=True,
                                        style={
                                            "width": "250px",
                                            "color": "black",
                                            "background-color": "white",
                                        },
                                    ),
                                    html.Img(
                                        id=f"team-sprite-{i}",
                                        src=None,
                                        style={
                                            "height": mon_height,
                                            "width": mon_width,
                                            "padding-top": "10px",
                                            "padding-left": "10px",  # Add padding to the left
                                        },
                                    ),
                                ],
                                width=2,
                            )
                            for i in range(6)
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    # team stats
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    id="expected-winrate",
                                    children="Expected Overall Winrate: ",
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                html.Div(
                                    id="avg-popularity", children="Average Popularity: "
                                ),
                                width=4,
                            ),
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    # DataFrame of Winrates into Top30
                    dbc.Row(
                        [
                            dbc.Col(
                                dash_table.DataTable(
                                    id="winrate-data",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in [
                                            "Top30 Most Popular Mons",
                                            "Top30 Mon Popularity (%)",
                                            "Top30 Mon General Winrate (%)",
                                            "Team Winrate x Top30 Mon (%)",
                                        ]
                                    ],
                                    data=[],
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(48, 48, 48)",
                                        }
                                    ],
                                    style_header={
                                        "backgroundColor": "rgb(30, 30, 30)",
                                        "color": "white",
                                        "textAlign": "center",  # Center the column titles
                                    },
                                    style_cell={
                                        "backgroundColor": "rgb(50, 50, 50)",
                                        "color": "white",
                                        "minWidth": "0px",
                                        "maxWidth": "180px",  # Adjust column widths
                                        "whiteSpace": "normal",  # Allow the text to wrap
                                        "textAlign": "center",  # Center the cell values
                                        "padding": "10px",  # Add padding to the cells
                                    },
                                ),
                            )
                        ]
                    ),
                ],
            ),
            html.Br(),
        ],
        className="bg-dark",
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
            "color": "white",
        },
    )


# pokemon selector options
@callback(
    [dash.dependencies.Output(f"pokemon-selector-0", "options")],
    [dash.dependencies.Output(f"pokemon-selector-1", "options")],
    [dash.dependencies.Output(f"pokemon-selector-2", "options")],
    [dash.dependencies.Output(f"pokemon-selector-3", "options")],
    [dash.dependencies.Output(f"pokemon-selector-4", "options")],
    [dash.dependencies.Output(f"pokemon-selector-5", "options")],
    [dash.dependencies.Input(f"dont-use-pokemon-selector", "value")],
    [dash.dependencies.Input(f"pokemon-selector-0", "value")],
    [dash.dependencies.Input(f"pokemon-selector-1", "value")],
    [dash.dependencies.Input(f"pokemon-selector-2", "value")],
    [dash.dependencies.Input(f"pokemon-selector-3", "value")],
    [dash.dependencies.Input(f"pokemon-selector-4", "value")],
    [dash.dependencies.Input(f"pokemon-selector-5", "value")],
    [dash.dependencies.State("viable-pokemon-store", "data")],
    order=1,
)
def update_pokemon_options(
    ignore_mons,
    mon0,
    mon1,
    mon2,
    mon3,
    mon4,
    mon5,
    viable_pokemon,
):
    mons = [mon0, mon1, mon2, mon3, mon4, mon5]

    selector_options = []
    for mon in mons:
        unavailable_mons = [other for other in mons if other not in [mon, None]]
        if ignore_mons is not None:
            unavailable_mons += ignore_mons

        selector_options.append(
            [
                {"label": pokemon_name, "value": pokemon_name}
                for pokemon_name in viable_pokemon
                if pokemon_name not in unavailable_mons
            ]
        )

    return (
        selector_options[0],
        selector_options[1],
        selector_options[2],
        selector_options[3],
        selector_options[4],
        selector_options[5],
    )


# pokemon sprites updates
@callback(
    [dash.dependencies.Output(f"pokemon-sprite-{i}", "src") for i in range(6)],
    [dash.dependencies.Input(f"pokemon-selector-{i}", "value") for i in range(6)],
    order=2,
)
def update_pokemon_sprites(*pokemon_names):
    return [
        find_closest_sprite(pokemon_name) if pokemon_name is not None else None
        for pokemon_name in pokemon_names
    ]


# update format data, viable mons, and mon selectors upon format change
@callback(
    [dash.dependencies.Output("viable-pokemon-store", "data")],
    [dash.dependencies.Output(f"pokemon-selector-0", "value")],
    [dash.dependencies.Output(f"pokemon-selector-1", "value")],
    [dash.dependencies.Output(f"pokemon-selector-2", "value")],
    [dash.dependencies.Output(f"pokemon-selector-3", "value")],
    [dash.dependencies.Output(f"pokemon-selector-4", "value")],
    [dash.dependencies.Output(f"pokemon-selector-5", "value")],
    [dash.dependencies.Output(f"dont-use-pokemon-selector", "options")],
    [dash.dependencies.Input("format-selector", "value")],
    order=0,
)
def update_viable_pokemon_store(selected_format):
    database_data = DatabaseData()
    format_data = FormatData(battle_format=selected_format, db=database_data)
    available_mons = format_data.get_format_available_mons()

    # don't use options
    dont_use_options = [
        {"label": pokemon_name, "value": pokemon_name}
        for pokemon_name in available_mons
    ]

    # upon a new format reset all selectors to None and update the format-data and available mons stores
    return (
        available_mons,
        None,
        None,
        None,
        None,
        None,
        None,
        dont_use_options,
    )


# build team script
@callback(
    [dash.dependencies.Output(f"team-mon-{i}", "value") for i in range(6)]
    + [dash.dependencies.Output(f"team-sprite-{i}", "src") for i in range(6)]
    + [
        dash.dependencies.Output("avg-popularity", "children"),
        dash.dependencies.Output("expected-winrate", "children"),
        dash.dependencies.Output("winrate-data", "data"),
    ]
    + [dash.dependencies.Input("build-team-button", "n_clicks")]
    + [dash.dependencies.State("creativity-input", "value")]
    + [dash.dependencies.State("dont-use-pokemon-selector", "value")]
    + [dash.dependencies.State("format-selector", "value")]
    + [dash.dependencies.State(f"pokemon-selector-{i}", "value") for i in range(6)],
)
def update_suggested_team(
    n_clicks, creativity, ignore_mons, battle_format, *selected_pokemon
):
    if n_clicks == 0:
        return [
            dash.no_update
        ] * 15  # Don't update anything if the button hasn't been clicked

    if not ignore_mons:
        ignore_mons = []

    format_data = FormatData(
        battle_format=battle_format,
        db=db_data,
    )
    # ------ solve for remainder of team and get display team info -------
    current_team = [pokemon for pokemon in selected_pokemon if pokemon is not None]
    team_solver = TeamSolver(
        db=db_data,
        battle_format=format_data.battle_format,
    )
    new_team = team_solver.solve_for_remainder_of_team(
        current_team=current_team,
        creativity=creativity,
        ignore_mons=ignore_mons,
        engine_name="antimeta",  # UPDATE WHEN NEW ENGINES AVAILABLE
    )
    display_team = DisplayTeam(
        team=new_team,
        engine="antimeta",  # UPDATE WHEN NEW ENGINES AVAILABLE
        format_data=format_data,
    )
    team_info_dict = display_team.get_display_information()

    # ------ prepare team info for display form-------

    suggested_names = [pokemon for pokemon in team_info_dict["team"]]
    suggested_sprites = [find_closest_sprite(name) for name in team_info_dict["team"]]

    avg_popularity = (
        f"Average Popularity: {round(team_info_dict['avg_popularity'], 2)}%"
    )
    expected_winrate = (
        f"Expected Overall Winrate: {round(team_info_dict['norm_winrate'], 2)}%"
    )
    winrate_data = team_info_dict["team info"]

    return (
        suggested_names
        + suggested_sprites
        + [
            avg_popularity,
            expected_winrate,
            winrate_data.to_dict("records"),
        ]
    )
