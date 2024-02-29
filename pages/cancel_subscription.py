# cancel_subscription.py
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from flask import session
from .navbar import navbar  # Ensure this import matches your project structure
from ninjackalytics.database.models import User, UserSubscriptions, SubscriptionTiers
from ninjackalytics.database.database import get_sessionlocal

dash.register_page(__name__, path="/cancel_subscription")


def layout():
    # Assuming 'username' in session indicates a logged-in user
    if "username" not in session:
        return dbc.Container(
            [
                navbar(),
                html.H2(
                    "Please log in to manage your subscription.",
                    style={"color": "white"},
                ),
                dbc.Button(
                    "Log In",
                    href="/account",
                    className="btn btn-primary",
                ),
            ],
            style=page_style(),
        )

    return dbc.Container(
        [
            navbar(),
            html.Div(
                [
                    html.H2("Cancel Subscription", style={"color": "white"}),
                    html.P(
                        "Are you sure you want to cancel your subscription? You will still have access to all features until your current subscription period ends.",
                        style={"color": "white"},
                    ),
                    dbc.Button(
                        "Confirm Cancellation",
                        id="confirm-cancellation-button",
                        className="btn btn-danger",
                    ),
                    dcc.Location(id="redirect-after-cancellation"),
                ],
                style=page_style(),
            ),
        ],
        fluid=True,
    )


@callback(
    Output("redirect-after-cancellation", "href"),
    Input("confirm-cancellation-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_cancellation(n_clicks):
    if n_clicks:
        with get_sessionlocal() as db_session:
            username = session["username"]
            user = db_session.query(User).filter_by(username=username).first()
            user_subscription = (
                db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
            )
            if user_subscription:
                user_subscription.cancelled = True
                db_session.commit()
        return "/account"
    return dash.no_update


def page_style():
    return {
        "background-image": "url('/assets/Background.jpg')",
        "background-size": "cover",
        "background-repeat": "no-repeat",
        "height": "100vh",
        "z-index": "0",
    }
