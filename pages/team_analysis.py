import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from .navbar import navbar
from .general_utility import find_closest_sprite
from .team_analysis_funcs import get_viable_formats, get_viable_pokemon

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
                html.Label(f"Pokemon {i+1}", style={"color": "white"}),
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
                            width=3,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Don't Use",
                                id=f"dont-use-pokemon-button-{i}",
                                n_clicks=0,
                                color="danger",
                                className="mr-1",
                                size="sm",
                                style={"margin-left": "10px"},
                            ),
                            width=2,
                        ),
                    ],
                ),
                html.Img(
                    id=f"pokemon-sprite-{i}",
                    src=None,
                    style={
                        "height": mon_height,
                        "width": mon_width,
                        "padding-top": "10px",
                    },
                ),
            ]
        )
        for i in range(6)
    ]
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
            html.Label("Pokemon Selections", style={"color": "white"}),
            *pokemon_selectors,
            html.Br(),
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


# define pokemon options based on format and other pokemon
for i in range(6):
    others = [x for x in range(6) if x != i]

    @callback(
        [dash.dependencies.Output(f"pokemon-selector-{i}", "options")],
        [dash.dependencies.Input("format-selector", "value")],
        [dash.dependencies.Input(f"dont-use-pokemon-selector", "value")],
        [dash.dependencies.Input(f"pokemon-selector-{others[0]}", "value")],
        [dash.dependencies.Input(f"pokemon-selector-{others[1]}", "value")],
        [dash.dependencies.Input(f"pokemon-selector-{others[2]}", "value")],
        [dash.dependencies.Input(f"pokemon-selector-{others[3]}", "value")],
        [dash.dependencies.Input(f"pokemon-selector-{others[4]}", "value")],
    )
    def update_pokemon_options(
        selected_format, ignore_mons, other1, other2, other3, other4, other5
    ):
        already_used_mons = [other1, other2, other3, other4, other5]

        pokemon_options = [
            {"label": pokemon_name, "value": pokemon_name}
            for pokemon_name in get_viable_pokemon(
                selected_format=selected_format,
                selected_ignore_mons=ignore_mons,
                already_used_mons=already_used_mons,
            )
        ]
        return [pokemon_options]


@callback(
    [dash.dependencies.Output(f"pokemon-sprite-{i}", "src") for i in range(6)],
    [dash.dependencies.Input(f"pokemon-selector-{i}", "value") for i in range(6)],
)
def update_pokemon_sprites(*pokemon_names):
    return [
        find_closest_sprite(pokemon_name) if pokemon_name is not None else None
        for pokemon_name in pokemon_names
    ]
