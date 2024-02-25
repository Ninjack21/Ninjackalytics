import dash
from dash import html, dcc, Input, Output, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from .navbar import navbar
from .page_utilities.general_utility import (
    find_closest_sprite,
    DatabaseData,
)
from typing import List, Tuple, Dict

dash.register_page(__name__, path="/meta_analysis")

mon_height = "85px"
mon_width = "85px"


def format_and_dependent_components(viable_formats):
    return dcc.Loading(
        id="loading-format-data-meta-analysis",
        children=[
            format_selector_component(viable_formats),
        ],
        type="circle",  # Loading spinner type
        fullscreen=False,  # Set to True to cover the whole screen while loading
        style={"color": "#FFFFFF"},  # Custom styles here
    )


# ============ Various Filters ============
def format_selector_component(viable_formats, selected_format=None):
    return html.Div(
        [
            html.Label("Format", style={"color": "white"}),
            dcc.Dropdown(
                id="format-selector-meta-analysis",
                options=[{"label": f, "value": f} for f in viable_formats],
                value=selected_format,
                placeholder="Select a format",  # Placeholder text
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
        ]
    )


def popularity_slider_component():
    return html.Div(
        [
            html.Div(
                html.Label(
                    "Popularity Range", style={"color": "white", "text-align": "center"}
                ),
                style={"margin-bottom": "10px"},
            ),
            dcc.RangeSlider(
                id="popularity-range-slider",
                min=0,
                max=100,
                step=1,
                value=[20, 100],  # Initial range set from 0% to 100%
                marks={i: str(i) for i in range(0, 101, 20)},
                allowCross=False,
            ),
            # This Div will display the dynamically updated range values
            html.Div(
                id="popularity-range-display",
                style={"color": "white", "marginTop": "20px", "text-align": "center"},
            ),
        ],
        style={"margin": "20px 0px"},  # Adjust spacing around the slider
    )


def winrate_slider_component():
    return html.Div(
        [
            html.Div(
                html.Label(
                    "Winrate Range", style={"color": "white", "text-align": "center"}
                ),
                style={"margin-bottom": "10px"},
            ),
            dcc.RangeSlider(
                id="winrate-range-slider",
                min=0,
                max=100,
                step=1,
                value=[0, 100],
                marks={i: str(i) for i in range(0, 101, 20)},
                allowCross=False,
            ),
            # This Div will display the dynamically updated range values
            html.Div(
                id="winrate-range-display",
                style={"color": "white", "marginTop": "20px", "text-align": "center"},
            ),
        ],
        style={"margin": "20px 0px"},  # Adjust spacing around the slider
    )


def choose_display_rows_component():
    return html.Div(
        [
            html.Div(
                html.Label(
                    "Number of Rows to Display",
                    style={"color": "white", "text-align": "center"},
                ),
                style={"margin-bottom": "10px"},
            ),
            dcc.Dropdown(
                id="display-rows-dropdown",
                options=[
                    {"label": "5", "value": 5},
                    {"label": "10", "value": 10},
                    {"label": "20", "value": 20},
                    {"label": "50", "value": 50},
                    {"label": "100", "value": 100},
                ],
                value=10,
                style={"width": "375px", "color": "black", "background-color": "white"},
            ),
            html.Br(),
        ]
    )


# ============ Dynamic Content ============
def generate_table(
    selected_format,
    lower_upper_pop=None,
    lower_upper_wr=None,
    page_size=10,
):
    db = DatabaseData(selected_format)
    pvpmetadata = db.get_pvpmetadata()
    pokemonmetadata = db.get_pokemonmetadata()

    pokemonmetadata = filter_pokemon_metadata(
        pokemonmetadata, lower_upper_pop, lower_upper_wr
    )

    # default sort by popularity
    pokemonmetadata = pokemonmetadata.sort_values(by="Popularity", ascending=False)

    # get the mons for the current page
    all_mons = list(pokemonmetadata["Pokemon"].unique())

    mons2bestworst = {mon: calculate_matchups(pvpmetadata, mon) for mon in all_mons}

    columns = [
        {"name": "Sprite", "id": "Pokemon_Sprite", "presentation": "markdown"},
        {"name": "Pokemon", "id": "Pokemon"},
        {"name": "Winrate", "id": "Winrate"},
        {"name": "Popularity", "id": "Popularity"},
        {
            "name": "Best Matchup Sprite",
            "id": "Best_Matchup_Sprite",
            "presentation": "markdown",
        },
        {"name": "Best Matchup", "id": "Best Matchup"},
        {
            "name": "Worst Matchup Sprite",
            "id": "Worst_Matchup_Sprite",
            "presentation": "markdown",
        },
        {"name": "Worst Matchup", "id": "Worst Matchup"},
    ]
    data = create_table_data(all_mons, pokemonmetadata, mons2bestworst)

    return create_datatable(columns, data, page_size)


def filter_pokemon_metadata(pokemonmetadata, lower_upper_pop=None, lower_upper_wr=None):
    if lower_upper_pop:
        # find the max popularity
        max_pop = pokemonmetadata["Popularity"].max()
        # convert the lower and upper bounds to represent %s of max
        lower_upper_pop = (
            max_pop * lower_upper_pop[0] / 100,
            max_pop * lower_upper_pop[1] / 100,
        )

        pokemonmetadata = pokemonmetadata[
            (pokemonmetadata["Popularity"] >= lower_upper_pop[0])
            & (pokemonmetadata["Popularity"] <= lower_upper_pop[1])
        ]
    if lower_upper_wr:
        pokemonmetadata = pokemonmetadata[
            (pokemonmetadata["Winrate"] >= lower_upper_wr[0])
            & (pokemonmetadata["Winrate"] <= lower_upper_wr[1])
        ]
    return pokemonmetadata


def calculate_matchups(pvpmetadata, pokemon):
    mon1_df = pvpmetadata[pvpmetadata["Pokemon1"] == pokemon]
    mon2_df = pvpmetadata[pvpmetadata["Pokemon2"] == pokemon]
    if mon1_df.empty and mon2_df.empty:
        return "No Data Found", "No Data Found"
    else:
        return find_best_worst_matchups(pvpmetadata, pokemon, mon1_df, mon2_df)


def find_best_worst_matchups(pvpmetadata, current_mon, mon1_df, mon2_df):
    mon1_df = pvpmetadata[pvpmetadata["Pokemon1"] == current_mon]
    mon2_df = pvpmetadata[pvpmetadata["Pokemon2"] == current_mon]
    if mon1_df.empty and mon2_df.empty:
        return ("No Data Found", "No Data Found")
    else:
        # P1 vs P2 is the winrate displayed, so look at each df's first and last idxs
        if not mon1_df.empty and not mon2_df.empty:
            # ------ best matchup -------
            mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[0]
            mon2_best = mon2_df.sort_values(by="Winrate", ascending=True).iloc[0]
            best_matchup = (
                mon1_best["Pokemon2"]
                if mon1_best["Winrate"] >= 1 - mon2_best["Winrate"]
                else mon2_best["Pokemon1"]
            )
            # ------ worst matchup -------
            mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[-1]
            mon2_best = mon2_df.sort_values(by="Winrate", ascending=True).iloc[-1]
            worst_matchup = (
                mon1_best["Pokemon2"]
                if mon1_best["Winrate"] <= 1 - mon2_best["Winrate"]
                else mon2_best["Pokemon1"]
            )
            return (best_matchup, worst_matchup)
        elif not mon1_df.empty:
            mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[0]
            mon1_worst = mon1_df.sort_values(by="Winrate", ascending=True).iloc[-1]
            return (mon1_best["Pokemon2"], mon1_worst["Pokemon2"])
        else:
            mon2_best = mon2_df.sort_values(by="Winrate", ascending=False).iloc[0]
            mon2_worst = mon2_df.sort_values(by="Winrate", ascending=True).iloc[-1]
            return (mon2_best["Pokemon1"], mon2_worst["Pokemon1"])


def generate_markdown_for_sprite(pokemon):
    sprite_url = find_closest_sprite(pokemon)
    return f"![{pokemon}]({sprite_url})"


def create_table_data(all_mons, pokemonmetadata, mons2bestworst):
    data = []
    for mon in all_mons:
        row = {
            "Pokemon_Sprite": generate_markdown_for_sprite(mon),
            "Pokemon": mon,
            "Winrate": f"{pokemonmetadata[pokemonmetadata['Pokemon'] == mon]['Winrate'].values[0]}%",
            "Popularity": f"{pokemonmetadata[pokemonmetadata['Pokemon'] == mon]['Popularity'].values[0]}%",
            "Best_Matchup_Sprite": generate_markdown_for_sprite(mons2bestworst[mon][0]),
            "Best Matchup": mons2bestworst[mon][0],
            "Worst_Matchup_Sprite": generate_markdown_for_sprite(
                mons2bestworst[mon][1]
            ),
            "Worst Matchup": mons2bestworst[mon][1],
        }
        data.append(row)
    return data


def create_datatable(columns, data, page_size=10):
    table = dash_table.DataTable(
        id="meta-analysis-table",
        columns=columns,
        data=data,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        style_data_conditional=[
            {"if": {"column_id": c}, "textAlign": "left"}
            for c in ["Pokemon", "Best Counter", "Worst Counter"]
        ],
        style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
        style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
        # Enable pagination
        page_action="native",
        page_size=page_size,
        page_current=0,
        sort_action="native",
    )

    return table


# ============ Layout ============


def layout():
    db_data = DatabaseData()
    viable_formats = db_data.viable_formats
    # simple layout with navbar and a title
    return html.Div(
        [
            navbar(),
            html.H1("Meta Analysis"),
            dbc.Row(  # Add this row to contain the filters
                [
                    dbc.Col(format_selector_component(viable_formats), width=3),
                    dbc.Col(popularity_slider_component(), width=3),
                    dbc.Col(winrate_slider_component(), width=3),
                    dbc.Col(choose_display_rows_component(), width=3),
                ],
                justify="center",  # Adjust the positioning (start, center, end, between, around)
            ),
            dcc.Loading(
                id="loading-format-data-meta-analysis",
                children=[
                    # The dynamic content will be updated via callbacks
                    html.Div(id="dynamic-content-meta-analysis"),
                ],
                type="circle",
                fullscreen=False,  # Change to `True` for fullscreen loading indicator
                color="#FFFFFF",
            ),
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


# ======================= Callbacks =======================
@callback(
    dash.dependencies.Output("popularity-range-display", "children"),
    [dash.dependencies.Input("popularity-range-slider", "value")],
)
def update_popularity_range(value):
    return (
        f"Selected Popularity Range: {value[0]}% - {value[1]}% of Max Seen Popularity"
    )


@callback(
    dash.dependencies.Output("winrate-range-display", "children"),
    [dash.dependencies.Input("winrate-range-slider", "value")],
)
def update_winrate_range(value):
    return f"Selected Winrate Range: {value[0]}% - {value[1]}%"


@callback(
    Output("dynamic-content-meta-analysis", "children"),
    [
        Input("format-selector-meta-analysis", "value"),
        Input("popularity-range-slider", "value"),
        Input("winrate-range-slider", "value"),
        Input("display-rows-dropdown", "value"),
    ],
)
def update_table(selected_format, popularity_range, winrate_range, page_size):
    if selected_format is None:
        return no_update
    else:
        return generate_table(
            selected_format, popularity_range, winrate_range, page_size
        )
