from flask import session
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import SubscriptionTiers, PromoCodeLinks
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
            html.H2("Submit Promo Code", style={"color": "white"}),
            html.Div(
                [
                    dcc.Input(
                        id="promo-code-input",
                        type="text",
                        placeholder="Enter Promo Code",
                        className="mb-3",
                    ),
                    html.Button(
                        "Submit Promo Code", id="submit-promo-code", n_clicks=0
                    ),
                    html.Div(id="promo-code-feedback", style={"color": "white"}),
                    # Placeholder for PayPal buttons (iFrame)
                    html.Div(id="paypal-buttons-container"),
                ],
                style={"margin-bottom": "50px"},  # Add some spacing between sections
            ),
            html.H2(
                "Or Select Your Desired Subscription Tier", style={"color": "white"}
            ),
            html.Div(
                [
                    dcc.Dropdown(
                        id="subscription-tier-dropdown",
                        options=tier_options,
                        className="mb-3",
                    ),
                    # Placeholder for future tier selection handling
                    html.Div(id="tier-selection-feedback", style={"color": "white"}),
                ]
            ),
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
    [
        Output("promo-code-feedback", "children"),
        Output("paypal-buttons-container", "children"),
    ],
    Input("submit-promo-code", "n_clicks"),
    State("promo-code-input", "value"),
)
def process_promo_code_submission(n_clicks, promo_code):
    if n_clicks > 0:
        with get_sessionlocal() as db_session:
            promo_code_link = (
                db_session.query(PromoCodeLinks)
                .filter_by(promo_code=promo_code)
                .first()
            )
            if promo_code_link:
                # iFrame to render PayPal buttons
                return "Promo code applied successfully."
            else:
                return "Invalid promo code. Please try again.", None
    return no_update, no_update
