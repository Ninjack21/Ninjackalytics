from flask import session
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import SubscriptionTiers
from ninjackalytics.database.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

# Assuming your Dash app is already set up
dash.register_page(__name__, path="/upgrade_account")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div

    # Fetch subscription tiers from the database\
    with get_sessionlocal() as db_session:
        subscription_tiers = db_session.query(SubscriptionTiers).all()
    tier_options = [
        {"label": f"{tier.product} - {tier.plan}", "value": f"{tier.id}"}
        for tier in subscription_tiers
    ]

    return html.Div(
        [
            navbar(),
            html.H1("Upgrade Your Account", style={"color": "white"}),
            html.Div(
                [
                    html.Label("Select a Subscription Tier", style={"color": "white"}),
                    dcc.Dropdown(
                        id="subscription-tier-dropdown",
                        options=tier_options,
                        className="mb-3",
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label("Enter Promo Code (if any)", style={"color": "white"}),
                    dcc.Input(
                        id="promo-code-input",
                        type="text",
                        placeholder="Promo Code",
                        className="mb-3",
                    ),
                ]
            ),
            html.Button("Submit", id="submit-upgrade", n_clicks=0),
            html.Div(id="upgrade-feedback", style={"color": "white"}),
        ],
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
            "color": "white",
        },
    )


@callback(
    Output("upgrade-feedback", "children"),
    Input("submit-upgrade", "n_clicks"),
    State("subscription-tier-dropdown", "value"),
    State("promo-code-input", "value"),
)
def process_upgrade(n_clicks, tier_id, promo_code):
    if n_clicks > 0:
        # Process the upgrade here
        # This is where you'd include logic to handle the upgrade, potentially
        # using the promo code and selected tier.
        return "Upgrade process initiated. Please check your email for confirmation."
    return no_update
