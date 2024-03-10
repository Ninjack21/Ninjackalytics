from flask import session
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from .navbar import navbar
from .page_utilities.general_utility import find_closest_sprite
from .page_utilities.team_classes import (
    DatabaseData,
    FormatData,
    TeamSolver,
    DisplayTeam,
)
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/team_analysis")

mon_height = "85px"
mon_width = "85px"


def format_and_dependent_components(viable_formats):
    return dcc.Loading(
        id="loading-format-data",
        children=[
            html.Div(
                "retrieving data from db, one moment...",
                style={"color": "white", "textAlign": "center"},
            ),
            format_selector_component(viable_formats),
            # Assume pokemon_selections_component and dont_use_pokemon_component depend on the selected format
            pokemon_selections_component([]),  # Initially empty, filled via callback
            dont_use_pokemon_component([]),  # Initially empty, filled via callback
        ],
        type="circle",  # Loading spinner type
        fullscreen=False,  # Set to True to cover the whole screen while loading
        style={"color": "#FFFFFF"},  # Custom styles here
    )


# ============ Format and Pokemon Selections ============
def format_selector_component(viable_formats, selected_format=None):
    return html.Div(
        [
            html.Label("Format", style={"color": "white"}),
            dcc.Dropdown(
                id="format-selector",
                options=[{"label": f, "value": f} for f in viable_formats],
                value=selected_format,
                placeholder="Select a format",  # Placeholder text
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
        ]
    )


def pokemon_selections_component(format_mons):
    return html.Div(
        [
            html.Label("Pokemon Selections", style={"color": "white"}),
            dbc.Row([pokemon_selector_col(i, format_mons) for i in range(6)]),
            html.Br(),
        ]
    )


def pokemon_selector_col(index, format_mons):
    return dbc.Col(
        [
            dcc.Dropdown(
                id=f"pokemon-selector-{index}",
                options=[
                    {"label": pokemon_name, "value": pokemon_name}
                    for pokemon_name in format_mons
                ],
                value=None,
                placeholder="Select a Pokemon",
                style={"width": "250px", "color": "black", "background-color": "white"},
            ),
            html.Img(
                id=f"pokemon-sprite-{index}",
                src=None,
                style={
                    "height": mon_height,
                    "width": mon_width,
                    "padding-top": "10px",
                    "padding-left": "10px",
                },
            ),
        ],
        width=2,
    )


def dont_use_pokemon_component(format_mons):
    return html.Div(
        [
            html.Label("Don't Use Pokemon", style={"color": "white"}),
            dcc.Dropdown(
                id="dont-use-pokemon-selector",
                options=[
                    {"label": pokemon_name, "value": pokemon_name}
                    for pokemon_name in format_mons
                ],
                multi=True,
                placeholder="Select Pokemon",
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
        ]
    )


def build_team_button_and_creativity_input_component():
    return html.Div(
        [
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
            dbc.Button(
                "Build Team",
                id="build-team-button",
                n_clicks=0,
                color="primary",
                className="mr-1",
            ),
            # Add a text note here
            html.Span(
                " This process generally takes less than a minute. Please be patient.",
                style={
                    "color": "white",
                    "margin-left": "10px",  # Add some spacing between the button and the text
                },
            ),
            html.Br(),
        ]
    )


# ============ Completed Team ============
def completed_team_component():
    return html.Div(
        [
            html.Label("Completed Team", style={"color": "white"}),
            dcc.Loading(
                id="loading",
                type="circle",
                children=[
                    # Suggested team and sprites
                    suggested_team_and_sprites(),
                    html.Br(),
                    # Team stats
                    team_stats(),
                    html.Br(),
                    # DataFrame of Winrates into Top30
                    winrate_data_table(),
                ],
            ),
            html.Br(),
        ]
    )


def suggested_team_and_sprites():
    return dbc.Row(
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
                            "padding-left": "10px",
                        },
                    ),
                ],
                width=2,
            )
            for i in range(6)
        ]
    )


def team_stats():
    return dbc.Row(
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
                    id="avg-popularity",
                    children="Average Popularity: ",
                ),
                width=4,
            ),
        ]
    )


def winrate_data_table():
    return dbc.Row(
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
                        },
                    ],
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                        "textAlign": "center",
                    },
                    style_cell={
                        "backgroundColor": "rgb(50, 50, 50)",
                        "color": "white",
                        "minWidth": "0px",
                        "maxWidth": "180px",
                        "whiteSpace": "normal",
                        "textAlign": "center",
                        "padding": "10px",
                    },
                ),
            )
        ]
    )


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_data = DatabaseData()
    viable_formats = db_data.viable_formats

    # The initial call to get_format_available_mons() is removed to avoid loading data at layout definition time.
    return html.Div(
        [
            navbar(),
            dcc.Store(id="viable-pokemon-store"),  # Initially empty
            html.H1("Team Builder Tool"),
            dcc.Loading(
                id="loading-format-data",
                children=[
                    format_selector_component(viable_formats),
                    # The components below will be dynamically filled via callbacks
                    html.Div(
                        id="dynamic-content",
                    ),
                ],
                fullscreen=False,  # Change to `True` for fullscreen loading indicator
            ),
        ],
        className="bg-dark",
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "min-height": "100vh",
            "z-index": "0",
            "color": "white",
        },
    )


# dynamically load content once viable format is selected
@callback(
    Output("dynamic-content", "children"),
    [Input("format-selector", "value")],
    order=1,
)
def update_dynamic_content(selected_format):
    if not selected_format:
        # Return a placeholder or empty content if no format is selected
        initial_content = html.Div(
            [
                pokemon_selections_component(["Choose a Format!"]),
                dont_use_pokemon_component(["Choose a Format!"]),
                build_team_button_and_creativity_input_component(),
                completed_team_component(),
            ]
        )
        return initial_content

    # Assuming you have functions to fetch data based on the selected format
    db_data = DatabaseData(format=selected_format)
    format_data = FormatData(battle_format=selected_format, db=db_data)
    format_mons = format_data.get_format_available_mons()

    # Now, populate the components that depend on the selected format
    content = html.Div(
        [
            pokemon_selections_component(format_mons),
            dont_use_pokemon_component(format_mons),
            build_team_button_and_creativity_input_component(),
            completed_team_component(),  # Ensure this component can handle being initially empty
        ]
    )

    return content


# pokemon selector options
@callback(
    [Output(f"pokemon-selector-{i}", "options") for i in range(6)],
    [Input(f"dont-use-pokemon-selector", "value")],
    State("viable-pokemon-store", "data"),
    [Input(f"pokemon-selector-{i}", "value") for i in range(6)],
    prevent_initial_call=True,  # Prevents the callback from running on initial load
    order=2,
)
def update_pokemon_options(ignore_mons, viable_mons, *selected_mons):
    # Check if viable_pokemon data is not loaded yet
    if not viable_mons:
        return [no_update] * 6  # Return no_update for all dropdowns

    # Build options considering ignore_mons and already selected mons
    selector_options = []
    for mon in selected_mons:
        unavailable_mons = [
            other for other in selected_mons if other not in [mon, None]
        ]
        if ignore_mons:
            unavailable_mons += ignore_mons

        options = [
            {"label": pokemon_name, "value": pokemon_name}
            for pokemon_name in viable_mons
            if pokemon_name not in unavailable_mons
        ]
        selector_options.append(options)

    return selector_options


# pokemon sprites updates
@callback(
    [Output(f"pokemon-sprite-{i}", "src") for i in range(6)],
    [Input(f"pokemon-selector-{i}", "value") for i in range(6)],
    order=3,
)
def update_pokemon_sprites(*pokemon_names):
    # Check if all pokemon_names are None (no Pokémon has been selected)
    if all(name is None for name in pokemon_names):
        # Return no_update for each sprite, indicating no change should be made
        return [no_update] * 6

    # Otherwise, proceed with updating sprites as before
    return [
        find_closest_sprite(pokemon_name) if pokemon_name is not None else None
        for pokemon_name in pokemon_names
    ]


# update format data, viable mons, and mon selectors upon format change
@callback(
    [Output("viable-pokemon-store", "data")],
    [Output(f"pokemon-selector-0", "value")],
    [Output(f"pokemon-selector-1", "value")],
    [Output(f"pokemon-selector-2", "value")],
    [Output(f"pokemon-selector-3", "value")],
    [Output(f"pokemon-selector-4", "value")],
    [Output(f"pokemon-selector-5", "value")],
    [Output(f"dont-use-pokemon-selector", "options")],
    [Input("format-selector", "value")],
    prevent_initial_call=True,  # Prevents the callback from running on initial load
    order=0,
)
def update_viable_pokemon_store(selected_format):
    if selected_format is None:
        # Return no_update for each sprite, indicating no change should be made
        return [no_update] * 8

    database_data = DatabaseData(format=selected_format)
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
    [Output(f"team-mon-{i}", "value") for i in range(6)]
    + [Output(f"team-sprite-{i}", "src") for i in range(6)]
    + [
        Output("avg-popularity", "children"),
        Output("expected-winrate", "children"),
        Output("winrate-data", "data"),
    ]
    + [Input("build-team-button", "n_clicks")]
    + [State("creativity-input", "value")]
    + [State("dont-use-pokemon-selector", "value")]
    + [State("format-selector", "value")]
    + [State(f"pokemon-selector-{i}", "value") for i in range(6)],
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

    db_data = DatabaseData(format=battle_format)
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
    # only show the top 10
    winrate_data = team_info_dict["team info"].head(10)

    return (
        suggested_names
        + suggested_sprites
        + [
            avg_popularity,
            expected_winrate,
            winrate_data.to_dict("records"),
        ]
    )
