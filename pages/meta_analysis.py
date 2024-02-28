from flask import session
import pandas as pd
import dash
from dash import html, dcc, Input, Output, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from .navbar import navbar
from .page_utilities.general_utility import (
    find_closest_sprite,
    DatabaseData,
)
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/meta_analysis")


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
    pvpmetadata,
    pokemonmetadata,
    lower_upper_pop=None,
    lower_upper_wr=None,
    page_size=10,
):

    filt_monmetadata = filter_pokemon_metadata(
        pokemonmetadata, lower_upper_pop, lower_upper_wr
    )

    # default sort by popularity
    filt_monmetadata = filt_monmetadata.sort_values(by="Popularity", ascending=False)

    all_mons = list(filt_monmetadata["Pokemon"].unique())
    filt_pvpmetadata = pvpmetadata[
        pvpmetadata["Pokemon1"].isin(all_mons) & pvpmetadata["Pokemon2"].isin(all_mons)
    ]

    mons2bestworst = {
        mon: calculate_matchups(filt_pvpmetadata, filt_monmetadata, mon)
        for mon in all_mons
    }

    columns = [
        {"name": "Sprite", "id": "Pokemon_Sprite", "presentation": "markdown"},
        {"name": "Pokemon", "id": "Pokemon"},
        {"name": "Winrate", "id": "Winrate"},
        {"name": "Popularity", "id": "Popularity"},
        # ------ worst matchup ------
        {
            "name": "Worst Matchup Sprite",
            "id": "Worst_Matchup_Sprite",
            "presentation": "markdown",
        },
        {"name": "Worst Matchup", "id": "Worst Matchup"},
        {"name": "Winrate into Worst Matchup", "id": "Winrate into Worst Matchup"},
        {
            "name": "Popularity of Worst Matchup Mon",
            "id": "Popularity of Worst Matchup Mon",
        },
        # ------ best matchup ------
        {
            "name": "Best Matchup Sprite",
            "id": "Best_Matchup_Sprite",
            "presentation": "markdown",
        },
        {"name": "Best Matchup", "id": "Best Matchup"},
        {"name": "Winrate into Best Matchup", "id": "Winrate into Best Matchup"},
        {
            "name": "Popularity of Best Matchup Mon",
            "id": "Popularity of Best Matchup Mon",
        },
    ]
    data = create_table_data(all_mons, pokemonmetadata, mons2bestworst)

    return create_datatable(columns, data, page_size)


def filter_pokemon_metadata(pokemonmetadata, lower_upper_pop=None, lower_upper_wr=None):
    copy_metadata = pokemonmetadata.copy()
    if lower_upper_pop:
        copy_metadata = copy_metadata[
            (copy_metadata["Popularity"] >= lower_upper_pop[0])
            & (copy_metadata["Popularity"] <= lower_upper_pop[1])
        ]
    if lower_upper_wr:
        copy_metadata = copy_metadata[
            (copy_metadata["Winrate"] >= lower_upper_wr[0])
            & (copy_metadata["Winrate"] <= lower_upper_wr[1])
        ]
    return copy_metadata


def calculate_matchups(pvpmetadata, pokemonmetadata, pokemon):
    pvp = pvpmetadata.copy()
    pvp = pvp[pvp["SampleSize"] >= 20]
    mon1_df = pvp[pvp["Pokemon1"] == pokemon]
    mon2_df = pvp[pvp["Pokemon2"] == pokemon]
    if mon1_df.empty and mon2_df.empty:
        return {
            "Best Matchup": ("No Data Found") * 3,
            "Worst Matchup": ("No Data Found") * 3,
        }
    else:
        return find_best_worst_matchups(pvp, pokemonmetadata, pokemon, mon1_df, mon2_df)


def find_best_worst_matchups(
    pvpmetadata, pokemonmetadata, current_mon, mon1_df, mon2_df
):

    mon1_df = pvpmetadata[pvpmetadata["Pokemon1"] == current_mon]
    mon2_df = pvpmetadata[pvpmetadata["Pokemon2"] == current_mon]
    # P1 vs P2 is the winrate displayed, so look at each df's first and last idxs
    if not mon1_df.empty and not mon2_df.empty:
        # ------ best matchup -------
        mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[0]
        mon2_best = mon2_df.sort_values(by="Winrate", ascending=True).iloc[0]
        if mon1_best["Winrate"] >= 100 - mon2_best["Winrate"]:
            best_matchup = (
                mon1_best["Pokemon2"],
                mon1_best["Winrate"],
                round(
                    pokemonmetadata[
                        pokemonmetadata["Pokemon"] == mon1_best["Pokemon2"]
                    ]["Popularity"].values[0],
                    2,
                ),
            )
        else:
            best_matchup = (
                mon2_best["Pokemon1"],
                100 - mon2_best["Winrate"],
                round(
                    pokemonmetadata[
                        pokemonmetadata["Pokemon"] == mon2_best["Pokemon1"]
                    ]["Popularity"].values[0],
                    2,
                ),
            )

        # ------ worst matchup -------
        mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[-1]
        mon2_best = mon2_df.sort_values(by="Winrate", ascending=True).iloc[-1]
        if mon1_best["Winrate"] <= 100 - mon2_best["Winrate"]:
            worst_matchup = (
                mon1_best["Pokemon2"],
                mon1_best["Winrate"],
                round(
                    pokemonmetadata[
                        pokemonmetadata["Pokemon"] == mon1_best["Pokemon2"]
                    ]["Popularity"].values[0],
                    2,
                ),
            )
        else:
            worst_matchup = (
                mon2_best["Pokemon1"],
                100 - mon2_best["Winrate"],
                round(
                    pokemonmetadata[
                        pokemonmetadata["Pokemon"] == mon2_best["Pokemon1"]
                    ]["Popularity"].values[0],
                    2,
                ),
            )
    elif not mon1_df.empty:
        mon1_best = mon1_df.sort_values(by="Winrate", ascending=False).iloc[0]
        mon1_worst = mon1_df.sort_values(by="Winrate", ascending=True).iloc[-1]
        best_matchup = (
            mon1_best["Pokemon2"],
            mon1_best["Winrate"],
            round(
                pokemonmetadata[pokemonmetadata["Pokemon"] == mon1_best["Pokemon2"]][
                    "Popularity"
                ].values[0],
                2,
            ),
        )
        worst_matchup = (
            mon1_worst["Pokemon2"],
            mon1_worst["Winrate"],
            round(
                pokemonmetadata[pokemonmetadata["Pokemon"] == mon1_worst["Pokemon2"]][
                    "Popularity"
                ].values[0],
                2,
            ),
        )
    else:
        mon2_best = mon2_df.sort_values(by="Winrate", ascending=False).iloc[0]
        mon2_worst = mon2_df.sort_values(by="Winrate", ascending=True).iloc[-1]
        best_matchup = (
            mon2_best["Pokemon1"],
            mon2_best["Winrate"],
            round(
                pokemonmetadata[pokemonmetadata["Pokemon"] == mon2_best["Pokemon1"]][
                    "Popularity"
                ].values[0],
                2,
            ),
        )
        worst_matchup = (
            mon2_worst["Pokemon1"],
            mon2_worst["Winrate"],
            round(
                pokemonmetadata[pokemonmetadata["Pokemon"] == mon2_worst["Pokemon1"]][
                    "Popularity"
                ].values[0],
                2,
            ),
        )
    return {
        "Best Matchup": best_matchup,
        "Worst Matchup": worst_matchup,
    }


def generate_markdown_for_sprite(pokemon):
    sprite_url = find_closest_sprite(pokemon)
    return f"![{pokemon}]({sprite_url})"


def create_table_data(all_mons, pokemonmetadata, mons2bestworst):
    data = []
    for mon in all_mons:
        row = {
            "Pokemon_Sprite": generate_markdown_for_sprite(mon),
            "Pokemon": mon,
            "Winrate": f"{round(pokemonmetadata[pokemonmetadata['Pokemon'] == mon]['Winrate'].values[0], 2)}%",
            "Popularity": f"{round(pokemonmetadata[pokemonmetadata['Pokemon'] == mon]['Popularity'].values[0], 2)}%",
            "Worst_Matchup_Sprite": generate_markdown_for_sprite(
                mons2bestworst[mon]["Worst Matchup"][0]
            ),
            "Worst Matchup": mons2bestworst[mon]["Worst Matchup"][0],
            "Winrate into Worst Matchup": mons2bestworst[mon]["Worst Matchup"][1],
            "Popularity of Worst Matchup Mon": mons2bestworst[mon]["Worst Matchup"][2],
            "Best_Matchup_Sprite": generate_markdown_for_sprite(
                mons2bestworst[mon]["Best Matchup"][0]
            ),
            "Best Matchup": mons2bestworst[mon]["Best Matchup"][0],
            "Winrate into Best Matchup": mons2bestworst[mon]["Best Matchup"][1],
            "Popularity of Best Matchup Mon": mons2bestworst[mon]["Best Matchup"][2],
        }
        data.append(row)
    return data


def create_datatable(columns, data, page_size=10):
    table = dash_table.DataTable(
        id="meta-analysis-table",
        columns=columns,
        data=data,
        style_table={
            "overflowX": "auto",
        },
        style_cell={
            "textAlign": "left",
            "minWidth": "100px",
            "maxWidth": "200px",
            "width": "150px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data_conditional=generate_style_data_conditional(columns),
        style_header={
            "backgroundColor": "rgb(30, 30, 30)",
            "color": "white",
            "fontWeight": "bold",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data={
            "backgroundColor": "rgb(50, 50, 50)",
            "color": "white",
        },
        # Enable pagination
        page_action="native",
        page_size=page_size,
        page_current=0,
        sort_action="native",  # Enables sorting
    )

    return table


def generate_style_data_conditional(columns):
    style_data_conditional = []

    for column in columns:
        column_id = column.get("id")
        if "Best Matchup" in column_id:
            style_data_conditional.append(
                {
                    "if": {"column_id": column_id},
                    "backgroundColor": "#ADD8E6",  # Light Blue for "Best Matchup"
                    "color": "black",
                }
            )
        elif "Worst Matchup" in column_id:
            style_data_conditional.append(
                {
                    "if": {"column_id": column_id},
                    "backgroundColor": "#FFA07A",  # Light Salmon for "Worst Matchup"
                    "color": "black",
                }
            )

        elif column_id in ["Pokemon", "Best Counter", "Worst Counter"]:
            style_data_conditional.append(
                {
                    "if": {"column_id": column_id},
                    "textAlign": "left",
                }
            )

    return style_data_conditional


# ============ Layout ============


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, "/meta_analysis"
    )
    if not access:
        return div

    db_data = DatabaseData()
    viable_formats = db_data.viable_formats
    # simple layout with navbar and a title
    return html.Div(
        [
            navbar(),
            dcc.Store("pvpmetadata-store"),
            dcc.Store("monmetadata-store"),
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
    [
        Output("pvpmetadata-store", "data"),
        Output("monmetadata-store", "data"),
    ],
    [Input("format-selector-meta-analysis", "value")],
)
def update_metadata_stores(selected_format):
    if selected_format is None:
        return no_update, no_update
    else:
        db = DatabaseData(selected_format)
        pvpmetadata = db.get_pvpmetadata()
        pokemonmetadata = db.get_pokemonmetadata()
        return pvpmetadata.to_dict("records"), pokemonmetadata.to_dict("records")


@callback(
    [
        Output("popularity-range-slider", "min"),
        Output("popularity-range-slider", "max"),
        Output("popularity-range-slider", "value"),
        Output("popularity-range-display", "children"),
    ],
    [Input("monmetadata-store", "data")],
    [Input("popularity-range-slider", "value")],
    order=1,
)
def update_slider_and_message(pokemonmetadata, selected_min_max_pop):
    if not pokemonmetadata:
        # Default values if no format is selected
        return 0, 100, [0, 100], "Please select a format to begin."

    pokemonmetadata = pd.DataFrame(pokemonmetadata)
    # Fetch data based on the selected format
    max_pop = pokemonmetadata["Popularity"].max()

    # Adjust the slider to the new max and update the message accordingly
    new_min = 0
    new_max = max_pop

    smin_pop, smax_pop = selected_min_max_pop[0], selected_min_max_pop[1]
    if smin_pop == 0 and smax_pop == 100:
        new_value = [
            10,
            max_pop,
        ]
        new_message = f"Selected Popularity Range: {new_value[0]}% - {new_value[1]}%"
    else:
        new_value = [smin_pop, smax_pop]
        new_message = f"Selected Popularity Range: {smin_pop}% - {smax_pop}%"

    return new_min, new_max, new_value, new_message


@callback(
    Output("winrate-range-display", "children"),
    [Input("winrate-range-slider", "value")],
    order=2,
)
def update_winrate_range(value):
    return f"Selected Winrate Range: {value[0]}% - {value[1]}%"


@callback(
    Output("dynamic-content-meta-analysis", "children"),
    [
        Input("pvpmetadata-store", "data"),
        Input("monmetadata-store", "data"),
        Input("popularity-range-slider", "value"),
        Input("winrate-range-slider", "value"),
        Input("display-rows-dropdown", "value"),
    ],
    order=0,
)
def update_table(pvpmetadata, monmetadata, popularity_range, winrate_range, page_size):
    if pvpmetadata is None:
        return no_update
    else:
        return generate_table(
            pd.DataFrame(pvpmetadata),
            pd.DataFrame(monmetadata),
            popularity_range,
            winrate_range,
            page_size,
        )
