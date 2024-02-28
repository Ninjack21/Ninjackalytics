from flask import session
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import (
    User,
    Roles,
    RolePages,
    SubscriptionTiers,
    SubscriptionPages,
    UserSubscription,
    Pages,
)
from .navbar import navbar

dash.register_page(__name__, path="/admin_home")

# Mapping of table classes to their human-readable names
TABLE_MAPPING = {
    "User": User,
    "Roles": Roles,
    "Pages": Pages,
    "RolePages": RolePages,
    "SubscriptionTiers": SubscriptionTiers,
    "SubscriptionPages": SubscriptionPages,
    "UserSubscription": UserSubscription,
}


def layout():
    table_options = [{"label": key, "value": key} for key in TABLE_MAPPING.keys()]
    return dbc.Container(
        [
            navbar(),
            html.H1("Database Management", style={"color": "white"}),
            dcc.Dropdown(
                id="table-selector", options=table_options, placeholder="Select a table"
            ),
            html.Div(id="navigation-area"),
        ],
        fluid=True,
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
        },
    )


@callback(Output("navigation-area", "children"), [Input("table-selector", "value")])
def update_navigation(selected_table):
    if not selected_table:
        return ""
    # Create a link or button for navigation
    path = f"/admin_{selected_table.lower()}"
    return dbc.Button(
        "Go to selected table", href=path, color="primary", external_link=True
    )
