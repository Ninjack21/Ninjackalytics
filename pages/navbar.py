import dash
from dash import html
import dash_bootstrap_components as dbc


def navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Team Builder", href="/team_analysis")),
            dbc.NavItem(dbc.NavLink("Meta Analysis", href="/meta_analysis")),
            dbc.NavItem(
                dbc.NavLink("Pre Battle Analysis", href="/pre_battle_analysis")
            ),
            dbc.NavItem(dbc.NavLink("Player Scout", href="/player_scout")),
            dbc.NavItem(dbc.NavLink("Account", href="/")),
        ],
        brand="Ninjackalytics",
        brand_href="/",
        color="dark",
        dark=True,
        fluid=True,
        className="navbar",
    )

    return navbar
