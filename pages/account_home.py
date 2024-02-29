from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from werkzeug.security import check_password_hash
from ninjackalytics.database.models import User, UserSubscriptions, SubscriptionTiers
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/account")


def manage_account_subscription_layout():
    username = session.get("username")
    # Initialize variables to avoid reference errors in case of missing subscription data
    subscription_tier_display = "No active subscription"
    subscription_type_display = "N/A"
    renewal_date_display = "N/A"
    cancellation_status = "N/A"
    renewal_cost = "N/A"

    with get_sessionlocal() as db_session:
        user = db_session.query(User).filter_by(username=username).first()
        if user:
            user_subscription = (
                db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
            )
            if user_subscription and user_subscription.active:
                subscription_tier = (
                    db_session.query(SubscriptionTiers)
                    .filter_by(id=user_subscription.subscription_tier_id)
                    .first()
                )
                subscription_type_display = user_subscription.subscription_type
                cancellation_status = (
                    "Cancelled" if user_subscription.cancelled else "Active"
                )
                show_uncancel_button = False
                if cancellation_status == "Active":
                    renewal_date_display = user_subscription.renewal_date.strftime(
                        "%B %d, %Y"
                    )
                    renewal_cost = (
                        f"${subscription_tier.monthly_cost}"
                        if user_subscription.subscription_type == "Monthly"
                        else f"${subscription_tier.annual_cost}"
                    )
                else:
                    show_uncancel_button = True
                    renewal_cost = "N/A"
                    renewal_date_display = (
                        "Your subscription will end on: "
                        + f"{user_subscription.renewal_date.strftime('%B %d, %Y')}"
                    )
                subscription_tier_display = (
                    subscription_tier.tier if subscription_tier else "Unknown tier"
                )

    if show_uncancel_button:
        return dbc.Container(
            [
                html.Div(
                    [
                        html.H2(
                            "Manage Subscription",
                            style={"color": "white", "marginBottom": "20px"},
                        ),
                        html.Div(
                            f"Subscription Tier: {subscription_tier_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Payment Frequency: {subscription_type_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Renewal Cost: {renewal_cost}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Subscription End / Renewal Date: {renewal_date_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Status: {cancellation_status}",
                            style={"color": "white", "marginBottom": "20px"},
                        ),
                        dbc.Button(
                            "Upgrade Subscription! 🥳",
                            href="/upgrade_account",
                            className="mt-3",
                            color="success",
                        ),
                        dbc.Button(
                            "Cancel Subscription | bye, friend 😔",
                            href="/cancel_subscription",
                            className="mt-3",
                            color="danger",
                        ),
                        dbc.Button(
                            "Renew Subscription | Welcome back, friend 🥲",
                            id="renew-subscription-button",
                            className="mt-3",
                            color="success",
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "borderRadius": "5px",
                        "background": "#000000a0",
                    },
                ),
            ],
            fluid=True,
            className="mt-3",
        )
    else:
        return dbc.Container(
            [
                html.Div(
                    [
                        html.H2(
                            "Manage Subscription",
                            style={"color": "white", "marginBottom": "20px"},
                        ),
                        html.Div(
                            f"Subscription Tier: {subscription_tier_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Payment Frequency: {subscription_type_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Renewal Cost: {renewal_cost}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Subscription End / Renewal Date: {renewal_date_display}",
                            style={"color": "white", "marginBottom": "10px"},
                        ),
                        html.Div(
                            f"Status: {cancellation_status}",
                            style={"color": "white", "marginBottom": "20px"},
                        ),
                        dbc.Button(
                            "Upgrade Subscription! 🥳",
                            href="/upgrade_account",
                            className="mt-3",
                            color="success",
                        ),
                        dbc.Button(
                            "Cancel Subscription | bye, friend 😔",
                            href="/cancel_subscription",
                            className="mt-3",
                            color="danger",
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "borderRadius": "5px",
                        "background": "#000000a0",
                    },
                ),
            ],
            fluid=True,
            className="mt-3",
        )


def layout():
    # Check if a user is logged in by looking for 'username' in session
    if "username" in session:
        username = session["username"]
        # Layout for logged-in users
        return dbc.Container(
            [
                navbar(),
                html.H1(
                    f"Hi {username}, this is your account page!",
                    style={"color": "white"},
                ),
                manage_account_subscription_layout(),
                dbc.Button("Logout", id="logout-button", className="mt-3"),
                dcc.Location(id="logout-redirect", refresh=True),
                dcc.Location(id="renew-redirect", refresh=True),
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
    else:
        # Layout for users who are not logged in
        return dbc.Container(
            [
                navbar(),
                html.H1("Login", style={"color": "white"}),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Username", style={"color": "white"}),
                                dbc.Input(
                                    id="login-username",
                                    type="text",
                                    placeholder="Username",
                                ),
                            ],
                            width=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Password", style={"color": "white"}),
                                dbc.Input(
                                    id="login-password",
                                    type="password",
                                    placeholder="Password",
                                ),
                            ],
                            width=4,
                        ),
                    ]
                ),
                dbc.Button("Login", id="login-button", className="mt-3"),
                html.Span(
                    id="login-output", className="mt-3", style={"color": "white"}
                ),
                html.Br(),
                dbc.Button(
                    "Create Account",
                    href="/register",
                    color="secondary",
                    className="mt-3",
                ),
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


@callback(
    Output("renew-redirect", "pathname"),
    Input("renew-subscription-button", "n_clicks"),
    prevent_initial_call=True,
)
def renew_subscription(n_clicks):
    if n_clicks:
        with get_sessionlocal() as db_session:
            username = session["username"]
            user = db_session.query(User).filter_by(username=username).first()
            user_subscription = (
                db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
            )
            if user_subscription:
                user_subscription.cancelled = False
                db_session.commit()
        return "/"
    return no_update


@callback(
    Output("logout-redirect", "pathname"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def logout(n_clicks):
    if n_clicks:
        session.pop("username", None)
        session.pop("role_id", None)
        session.pop("subscription_tier_id", None)
        return "/"
    return no_update
