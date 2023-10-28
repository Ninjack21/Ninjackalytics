import dash
from dash import html
import dash_bootstrap_components as dbc


def navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Submit Battle", href="/")),
        ],
        brand="Ninjackalytics",
        brand_href="/",
        color="primary",
        dark=True,
        fluid=True,
        className="navbar",
    )

    return navbar
