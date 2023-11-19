import dash
from dash import html
import dash_bootstrap_components as dbc


def navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Team Analysis", href="/team_analysis")),
        ],
        brand="Ninjackalytics",
        brand_href="/",
        color="dark",
        dark=True,
        fluid=True,
        className="navbar",
    )

    return navbar
