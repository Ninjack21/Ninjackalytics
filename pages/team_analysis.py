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
                dcc.Dropdown(
                    id=f"pokemon-selector-{i}",
                    options=[
                        {"label": pokemon_name, "value": pokemon_name}
                        for pokemon_name in get_viable_pokemon(
                            format_options[0]["value"]
                        )
                    ],
                    value=get_viable_pokemon(format_options[0]["value"])[i],
                    placeholder="fill for me",
                    style={
                        "width": "375px",
                        "color": "black",
                        "background-color": "white",
                    },
                ),
                html.Img(
                    id=f"pokemon-sprite-{i}",
                    src=find_closest_sprite(
                        get_viable_pokemon(format_options[0]["value"])[i]
                    ),
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


@callback(
    [dash.dependencies.Output(f"pokemon-selector-{i}", "options") for i in range(6)],
    [dash.dependencies.Input("format-selector", "value")],
)
def update_pokemon_options(selected_format):
    pokemon_options = [
        {"label": pokemon_name, "value": pokemon_name}
        for pokemon_name in get_viable_pokemon(selected_format)
    ]
    return [pokemon_options for _ in range(6)]


@callback(
    [dash.dependencies.Output(f"pokemon-sprite-{i}", "src") for i in range(6)],
    [dash.dependencies.Input(f"pokemon-selector-{i}", "value") for i in range(6)],
)
def update_pokemon_sprites(*pokemon_names):
    return [
        find_closest_sprite(pokemon_name) if pokemon_name is not None else None
        for pokemon_name in pokemon_names
    ]
