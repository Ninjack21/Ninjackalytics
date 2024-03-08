from flask import session
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import (
    SubscriptionTiers,
    PromoCodeLinks,
    UserSubscriptions,
    User,
)
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

    if not session.get("username"):
        return html.Div(
            [
                navbar(),
                html.H1(
                    "You must be logged in to upgrade your account",
                    style={"color": "white"},
                ),
                dbc.Button("Login", href="/login", color="primary"),
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

    with get_sessionlocal() as db_session:
        subscription_tiers = db_session.query(SubscriptionTiers).all()

    tier_options = [
        {"label": f"{tier.product} - {tier.plan}", "value": f"{tier.id}"}
        for tier in subscription_tiers
        if tier.product != "Free"
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
                        style={
                            "width": "50%",
                            "color": "black",
                            "align": "left",
                        },
                    ),
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
                # store promo code in session and redirect to paypal
                session["promo_code"] = promo_code
                already_have_active_subscription = check_for_active_subscription(
                    session.get("username")
                )
                if already_have_active_subscription:
                    return (
                        "You already have an active subscription."
                        + " Please cancel your current subscription before applying a new promo code."
                        + " Also, please note that at this time we do not have a way to upgrade a subscription"
                        + " from a lower tier to a higher tier. If you would like to, submit a contact us ticket"
                        + " and we will see what we can do. Thank you!",
                    )

                return (
                    html.A(
                        "Promo code accepted! Click here to upgrade your account.",
                        href=f"/upgrade_account_flask",
                        style={"color": "white"},
                    ),
                )
            else:
                return ("Invalid promo code. Please try again.",)

    return no_update


@callback(
    [
        Output("tier-selection-feedback", "children"),
    ],
    Input("subscription-tier-dropdown", "value"),
)
def process_tier_selection(tier_id):
    if tier_id:
        with get_sessionlocal() as db_session:
            promo_code_link = (
                db_session.query(PromoCodeLinks)
                .filter_by(subscription_tier_id=tier_id, advertiser="Default")
                .first()
            )
        if promo_code_link:
            # store promo code in session and redirect to paypal
            # NOTE: all paypal links have a "promo code" but these will select those
            # associated with the advertiser Default, which is yours truly
            session["promo_code"] = promo_code_link.promo_code
            already_have_active_subscription = check_for_active_subscription(
                session.get("username")
            )
            if already_have_active_subscription:
                return (
                    "You already have an active subscription."
                    + " Please cancel your current subscription before applying a new promo code."
                    + " Also, please note that at this time we do not have a way to upgrade a subscription"
                    + " from a lower tier to a higher tier. If you would like to, submit a contact us ticket"
                    + " and we will see what we can do. Thank you!",
                )

            return (
                html.A(
                    "Click here to upgrade your account.",
                    href=f"/upgrade_account_flask",
                    style={"color": "white"},
                ),
            )
        else:
            return ("Something went wrong, please try again or submit a ticket",)

    return no_update


# --------------- helper functions ----------------
def check_for_active_subscription(username):
    with get_sessionlocal() as db_session:
        user = db_session.query(User).filter_by(username=username).first()
        user_sub = (
            db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
        )
        print(user_sub)
        if user_sub is None:
            return False
        print(user_sub.active)
        return user_sub.active


def get_user_subscription_tier_id(user_id):
    with get_sessionlocal() as db_session:
        user_sub = (
            db_session.query(UserSubscriptions).filter_by(user_id=user_id).first()
        )
        return user_sub.subscription_tier_id
