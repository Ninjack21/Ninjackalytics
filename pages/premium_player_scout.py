from flask import session
import pandas as pd
import numpy as np
from datetime import date
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from .navbar import navbar
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
from .page_utilities.general_utility import (
    DatabaseData,
)
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)


dash.register_page(__name__, path="/player_scout")


def player_name_and_format_and_date_component(
    viable_formats, selected_format=None, selected_date=None
):
    component = dbc.Row(
        [
            dbc.Col(
                [
                    html.H3("Player Name"),
                    dbc.Input(
                        id="player_name",
                        type="text",
                        placeholder="Enter Player Name",
                        debounce=True,
                    ),
                ],
                width=3,
            ),
            dbc.Col(
                [
                    html.H3("Format"),
                    dbc.Select(
                        id="format",
                        options=[{"label": f, "value": f} for f in viable_formats],
                        value=selected_format,
                        placeholder="Select a Format",
                    ),
                ],
                width=3,
            ),
            dbc.Col(
                [
                    html.H3("Cutoff Date"),
                    dcc.DatePickerSingle(
                        id="date",
                        min_date_allowed=date(2023, 6, 1),  # Rough genesis date of tool
                        max_date_allowed=date.today(),  # Maximum date allowed, typically today
                        initial_visible_month=date.today(),  # Initially shown month when the calendar opens
                        date=selected_date,  # Selected date
                        placeholder="Select a Date",
                    ),
                ],
                width=4,
            ),
            dbc.Col(
                [
                    html.Div(),  # This ensures alignment with other columns
                    dbc.Button(
                        "Search", id="search_button", color="primary", className="mt-4"
                    ),
                ],
                width=2,
            ),
        ],
        className="m-2",
    )

    return component


def player_scout_dynamic_content(player_name, fmat, date):
    ta = TableAccessor()
    if date is None:
        battle_info_conditions = {
            "Format": {"op": "==", "value": fmat},
        }
    else:
        battle_info_conditions = {
            "Format": {"op": "==", "value": fmat},
            "Date_Submitted": {"op": ">=", "value": date},
        }

    battles = ta.get_battle_info(battle_info_conditions)

    p_battles = battles[(battles["P1"] == player_name) | (battles["P2"] == player_name)]
    if p_battles.empty:
        return "WARN"
    # p = player, o = opponent
    p_teams, o_teams = _get_p_teams_and_opp_teams_from_battle_info(
        player_name, p_battles, ta
    )
    p_teams_df, o_teams_df = _get_teams_data(p_teams, o_teams, p_battles, player_name)
    fig_usages, fig_winrates = _p_team_plots(p_teams_df)
    o_winrates = _o_team_plots(o_teams_df)
    replay_urls = _get_replay_urls(p_battles)

    return html.Div(
        [
            html.H3(f"Player Scout for {player_name}", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Graph(
                        figure=fig_usages,
                        style={
                            "width": "49%",
                            "minHeight": "400px",  # Specify a minimum height
                            "display": "inline-block",
                            "padding": "20px",
                        },
                    ),
                    dcc.Graph(
                        figure=fig_winrates,
                        style={
                            "width": "49%",
                            "minHeight": "400px",  # Specify the same minimum height
                            "display": "inline-block",
                            "padding": "20px",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "space-around",
                    "align-items": "stretch",
                },  # Use align-items: stretch for vertical alignment
            ),
            html.Div(
                [
                    dcc.Graph(
                        figure=o_winrates,
                        style={
                            "width": "49%",
                            "minHeight": "400px",  # Specify the same minimum height
                            "display": "inline-block",
                            "padding": "20px",
                        },
                    ),
                    # Adjusted to use the generate_replay_links_div function
                    _generate_replay_links_div(replay_urls),
                ],
                style={
                    "display": "flex",
                    "justify-content": "space-around",
                    "align-items": "stretch",
                },  # Ensure vertical alignment
            ),
        ]
    )


def _p_team_plots(p_teams_df):
    p_teams_df = p_teams_df.sort_values(by="Usage", ascending=False)
    p_teams_df = p_teams_df[p_teams_df["Usage"] >= 10]
    p_teams_df = p_teams_df.sort_values(by="Usage", ascending=False)

    unique_mons = p_teams_df["Mon"].unique()
    num_colors = len(unique_mons)
    colors = px.colors.sample_colorscale("Rainbow", np.linspace(0, 1, num_colors))
    mon_color_mapping = {mon: color for mon, color in zip(unique_mons, colors)}

    # ====== generate the plots ======
    fig_usage = go.Figure()
    fig_usage.add_trace(
        go.Bar(
            x=p_teams_df["Mon"],
            y=p_teams_df["Usage"],
            marker_color=[mon_color_mapping[mon] for mon in p_teams_df["Mon"]],
            name="Usage",
        )
    )
    fig_usage.update_layout(
        title="Favorite Pokemon by Usage (% of Teams)",
        xaxis_title="Pokemon",
        yaxis_title="Usage %",
        template="plotly_dark",
        barmode="group",
    )

    p_teams_df = p_teams_df.sort_values(by="Winrate", ascending=False)

    fig_winrate = go.Figure()
    fig_winrate.add_trace(
        go.Bar(
            x=p_teams_df["Mon"],
            y=p_teams_df["Winrate"],
            marker_color=[mon_color_mapping[mon] for mon in p_teams_df["Mon"]],
            name="Winrate",
        )
    )
    fig_winrate.update_layout(
        title="Favorite Pokemon's Winrates",
        xaxis_title="Pokemon",
        yaxis_title="Winrate %",
        template="plotly_dark",
        barmode="group",
    )
    return fig_usage, fig_winrate


def _o_team_plots(o_teams_df):
    threshold_wr = o_teams_df["Winrate"].quantile(0.75)
    o_teams_df = o_teams_df[
        (o_teams_df["Usage"] >= 5) & (o_teams_df["Winrate"] >= threshold_wr)
    ]
    unique_mons = o_teams_df["Mon"].unique()
    num_colors = len(unique_mons)
    colors = px.colors.sample_colorscale("Hot", np.linspace(0, 1, num_colors))
    mon_color_mapping = {mon: color for mon, color in zip(unique_mons, colors)}

    o_teams_df = o_teams_df.sort_values(by="Winrate", ascending=False)

    fig_winrate = go.Figure()
    fig_winrate.add_trace(
        go.Bar(
            x=o_teams_df["Mon"],
            y=o_teams_df["Winrate"],
            marker_color=[mon_color_mapping[mon] for mon in o_teams_df["Mon"]],
            name="Winrate",
        )
    )
    fig_winrate.update_layout(
        title="Player's Hardest Matchups<br>(i.e. higher winrate = player loses more to that mon)",
        xaxis_title="Pokemon",
        yaxis_title="Winrate %",
        template="plotly_dark",
        barmode="group",
    )
    return fig_winrate


def _get_replay_urls(pbattles):
    pbattles = pbattles.sort_values(by="Date_Submitted", ascending=False)
    bids = pbattles["Battle_ID"].unique()
    replay_urls = []
    for bid in bids:
        replay_urls.append(f"https://replay.pokemonshowdown.com/{bid}")

    return replay_urls


def _generate_replay_links_div(replay_urls):
    # Create a list of html.A components for each URL
    links_list = [
        html.A(
            url,
            href=url,
            target="_blank",
            style={"display": "block", "margin-bottom": "5px"},
        )
        for url in replay_urls
    ]

    # Wrap the links in a div with styling for scrolling
    return html.Div(
        links_list,
        style={
            "padding": "20px",
            "border": "solid",
            "height": "400px",
            "overflowY": "scroll",
        },
    )


def _get_p_teams_and_opp_teams_from_battle_info(player_name, battle_info, ta):
    p1_teams = battle_info[battle_info["P1"] == player_name]["P1_team"].unique()
    p2_teams = battle_info[battle_info["P2"] == player_name]["P2_team"].unique()

    p_teams_all = list(set(list(p1_teams) + list(p2_teams)))
    condition = {"id": {"op": "in", "value": p_teams_all}}
    p_teams = ta.get_teams(condition)

    opp_p1_teams = battle_info[battle_info["P1"] == player_name]["P2_team"].unique()
    opp_p2_teams = battle_info[battle_info["P2"] == player_name]["P1_team"].unique()
    opp_teams_all = list(set(list(opp_p1_teams) + list(opp_p2_teams)))
    condition = {"id": {"op": "in", "value": opp_teams_all}}
    o_teams = ta.get_teams(condition)

    return p_teams, o_teams


def _get_teams_data(p_teams, o_teams, battle_info, player_name):
    all_mons = pd.concat([p_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    # "|" in team mons used to be a problem, leaving here until more sure not an issue
    mons = [mon for mon in all_mons if mon != None and "|" not in mon]

    def contains_mon(row, mon):
        return mon in row.values

    p_mons2teamids = {
        mon: p_teams[
            p_teams.apply(
                lambda row: contains_mon(
                    row[["Pok1", "Pok2", "Pok3", "Pok4", "Pok5", "Pok6"]], mon
                ),
                axis=1,
            )
        ]["id"].tolist()
        for mon in mons
    }

    p_mons2usagewinrates = {
        mon: _get_usage_and_winrate(mon, p_mons2teamids, player_name, battle_info)
        for mon in mons
    }
    data = [
        {"Mon": mon, "Usage": usage_winrate[0], "Winrate": usage_winrate[1]}
        for mon, usage_winrate in p_mons2usagewinrates.items()
    ]
    p_teams_df = pd.DataFrame(data)

    all_mons = pd.concat([o_teams[f"Pok{i}"] for i in range(1, 7)]).unique()
    mons = [mon for mon in all_mons if mon != None and "|" not in mon]
    o_mons2teamids = {
        mon: o_teams[
            o_teams.apply(
                lambda row: contains_mon(
                    row[["Pok1", "Pok2", "Pok3", "Pok4", "Pok5", "Pok6"]], mon
                ),
                axis=1,
            )
        ]["id"].tolist()
        for mon in mons
    }
    o_mons2usagewinrates = {
        mon: _get_usage_and_winrate(
            mon, o_mons2teamids, player_name, battle_info, get_player_winrates=False
        )
        for mon in mons
    }

    data = [
        {"Mon": mon, "Usage": usage_winrate[0], "Winrate": usage_winrate[1]}
        for mon, usage_winrate in o_mons2usagewinrates.items()
    ]
    o_teams_df = pd.DataFrame(data)

    return p_teams_df, o_teams_df


def _get_usage_and_winrate(
    mon, mons2teamids, player_name, battle_info, get_player_winrates=True
):
    if get_player_winrates:
        teamids = mons2teamids[mon]
        all_battles = len(battle_info)
        if all_battles == 0:
            return 0, 0

        p1_teams_with_mon = battle_info[
            (battle_info["P1"] == player_name) & (battle_info["P1_team"].isin(teamids))
        ]
        p2_teams_with_mon = battle_info[
            (battle_info["P2"] == player_name) & (battle_info["P2_team"].isin(teamids))
        ]
        all_teams_with_mon = len(p1_teams_with_mon) + len(p2_teams_with_mon)

        mon_usage = round((all_teams_with_mon / all_battles) * 100, 2)

        p1_wins = len(p1_teams_with_mon[p1_teams_with_mon["Winner"] == player_name])
        p2_wins = len(p2_teams_with_mon[p2_teams_with_mon["Winner"] == player_name])

        mon_winrate = round((p1_wins + p2_wins) / all_teams_with_mon * 100, 2)

        return mon_usage, mon_winrate
    # else, get opponent winrates
    else:
        teamids = mons2teamids[mon]
        all_battles = len(battle_info)
        if all_battles == 0:
            return 0, 0
        # now find the battles where the player was against the current pokemon
        p1_teams_against_mon = battle_info[
            (battle_info["P1"] == player_name) & (battle_info["P2_team"].isin(teamids))
        ]
        p2_teams_against_mon = battle_info[
            (battle_info["P2"] == player_name) & (battle_info["P1_team"].isin(teamids))
        ]
        all_teams_with_mon = len(p1_teams_against_mon) + len(p2_teams_against_mon)

        # NOTE: this is technically not used as of 2-27-24
        mon_usage = round((all_teams_with_mon / all_battles) * 100, 2)

        # get the wins for the other player (who had the current mon in question)
        p2_wins = len(
            p1_teams_against_mon[p1_teams_against_mon["Winner"] != player_name]
        )
        p1_wins = len(
            p2_teams_against_mon[p2_teams_against_mon["Winner"] != player_name]
        )

        mon_winrate = round((p1_wins + p2_wins) / all_teams_with_mon * 100, 2)

        return mon_usage, mon_winrate


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_data = DatabaseData()
    viable_formats = db_data.get_viable_formats()
    return html.Div(
        [
            navbar(),
            html.H1("Player Scout"),
            html.Div(
                [
                    player_name_and_format_and_date_component(viable_formats),
                ],
                style={"width": "50%", "margin": "auto"},
            ),
            dcc.Loading(
                id="loading-dynamic-content",
                children=[html.Div(id="dynamic-content-player-scout")],
                type="circle",  # Choose the spinner style
                color="#FFFFFF",  # Customize the spinner color
                fullscreen=False,  # Set True for fullscreen loading, if needed
            ),
            dcc.ConfirmDialog(
                id="player-not-found-error-dialog",
                message=f"That player was not found in the database for the current format. We apologize for the inconvenience. Please try again with a different player or format.",
            ),
            dcc.ConfirmDialog(
                id="fill-all-fields-error-dialog",
                message="Please fill in the player name and format fields before clicking search.",
            ),
        ],
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "min-height": "100vh",
            "z-index": "0",
            "color": "white",
        },
    )


@callback(
    [
        Output("dynamic-content-player-scout", "children"),
        Output("player-not-found-error-dialog", "displayed"),
        Output("fill-all-fields-error-dialog", "displayed"),
    ],
    [
        Input("search_button", "n_clicks"),
    ],
    [
        State("player_name", "value"),
        State("format", "value"),
        State("date", "date"),
    ],
)
def update_dynamic_content(n_clicks, player_name, fmat, date):
    if n_clicks is None:
        return no_update, no_update, no_update

    if player_name is None or fmat is None:
        # If any of the fields are empty, show the error dialog for an empty field
        return no_update, False, True

    dynamic_content = player_scout_dynamic_content(player_name, fmat, date)
    if dynamic_content == "WARN":
        return no_update, True, False
    return dynamic_content, False, False
