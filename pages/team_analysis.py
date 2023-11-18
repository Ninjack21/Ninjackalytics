import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from .navbar import navbar
from .general_utility import find_closest_sprite
from .team_analysis_funcs import (
    get_viable_formats,
    get_viable_pokemon,
    get_viable_format_pokemon,
    solve_for_remainder_of_team,
)

dash.register_page(__name__, path="/team_analysis")

mon_height = "85px"
mon_width = "85px"


def layout():
    format_options = [
        {"label": format_name, "value": format_name}
        for format_name in get_viable_formats()
    ]
    pokemon_selectors = [
        html.Div(
            [
                dcc.Store(
                    id="viable-pokemon-store",
                    data=get_viable_format_pokemon(
                        selected_format=format_options[0]["value"]
                    ),
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"pokemon-selector-{i}",
                                options=[
                                    {"label": pokemon_name, "value": pokemon_name}
                                    for pokemon_name in get_viable_pokemon(
                                        selected_format=format_options[0]["value"],
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
                            width=6,
                        ),
                        dbc.Col(
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
                            width=6,
                            style={
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "flex-end",
                            },
                        ),
                    ],
                    style={"align-items": "center"},
                ),
            ],
            className="col-md-4",
            style={"display": "flex", "align-items": "center"},
        )
        for i in range(6)
    ]

    suggested_team = html.Div(
        [
            html.Div(
                [
                    html.H5(id=f"suggested-pokemon-name-{i}", children=""),
                    html.Img(
                        id=f"suggested-pokemon-sprite-{i}",
                        src=None,
                        style={
                            "height": mon_height,
                            "width": mon_width,
                            "padding-top": "10px",
                            "padding-left": "10px",
                        },
                    ),
                ],
                className="col-md-4",
                style={"display": "flex", "align-items": "center"},
            )
            for i in range(6)
        ],
        id="suggested-team",
    )
    return html.Div(
        [
            navbar(),
            html.H1("Team Builder Tool"),
            html.Br(),
            html.Label("Format", style={"color": "white"}),
            dcc.Dropdown(
                id="format-selector",
                options=format_options,
                value=format_options[0]["value"],
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
            # ===== POKEMON SELECTIONS ======
            html.Label("Pokemon Selections", style={"color": "white"}),
            *pokemon_selectors,
            html.Br(),
            # ===== DON'T USE POKEMON ======
            html.Label("Don't Use Pokemon", style={"color": "white"}),
            dcc.Dropdown(
                id="dont-use-pokemon-selector",
                options=[
                    {"label": pokemon_name, "value": pokemon_name}
                    for pokemon_name in get_viable_pokemon(
                        selected_format=format_options[0]["value"],
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
        ],
        className="bg-dark",
        style={
            "background-image": "url('/assets/background.jpg')",
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
    [dash.dependencies.Input("format-selector", "value")],
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
    selected_format,
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


@callback(
    Output("viable-pokemon-store", "data"),
    [dash.dependencies.Output(f"pokemon-selector-0", "value")],
    [dash.dependencies.Output(f"pokemon-selector-1", "value")],
    [dash.dependencies.Output(f"pokemon-selector-2", "value")],
    [dash.dependencies.Output(f"pokemon-selector-3", "value")],
    [dash.dependencies.Output(f"pokemon-selector-4", "value")],
    [dash.dependencies.Output(f"pokemon-selector-5", "value")],
    Input("format-selector", "value"),
    order=0,
)
def update_viable_pokemon_store(selected_format):
    return (
        get_viable_format_pokemon(selected_format=selected_format),
        None,
        None,
        None,
        None,
        None,
        None,
    )


@callback(
    [
        dash.dependencies.Output(f"suggested-pokemon-name-{i}", "children")
        for i in range(6)
    ]
    + [
        dash.dependencies.Output(f"suggested-pokemon-sprite-{i}", "src")
        for i in range(6)
    ],
    [dash.dependencies.Input("build-team-button", "n_clicks")],
    [dash.dependencies.Input("creativity-input", "value")],
    [dash.dependencies.Input("dont-use-pokemon-selector", "value")],
    [dash.dependencies.Input("format-selector", "value")],
    [dash.dependencies.State(f"pokemon-selector-{i}", "value") for i in range(6)],
)
def update_suggested_team(
    n_clicks, creativity, ignore_mons, battle_format, *selected_pokemon
):
    if n_clicks == 0:
        return [
            dash.no_update
        ] * 12  # Don't update anything if the button hasn't been clicked

    if not ignore_mons:
        ignore_mons = []
    # Generate your suggested team here. This is just a placeholder.
    current_team = [pokemon for pokemon in selected_pokemon if pokemon is not None]
    suggested_team = solve_for_remainder_of_team(
        current_team=current_team,
        battle_format=battle_format,
        creativity=creativity,
        ignore_mons=ignore_mons,
    )

    # Get the names and sprites of the suggested team
    suggested_names = suggested_team
    suggested_sprites = [find_closest_sprite(name) for name in suggested_team]

    return suggested_names + suggested_sprites
