from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from werkzeug.security import generate_password_hash, check_password_hash
from ninjackalytics.database.models import User, UserSubscriptions, SubscriptionTiers
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/account")


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
                # Add more account management options here
                dbc.Button("Logout", id="logout-button", className="mt-3"),
                dcc.Location(id="logout-redirect", refresh=True),
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
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    [State("login-username", "value"), State("login-password", "value")],
    prevent_initial_call=True,
)
def login(n_clicks, username, password):
    if n_clicks is None or n_clicks < 1:
        return no_update
    with get_sessionlocal() as db_session:
        user = db_session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.hashed_password, password):
            user_sub = (
                db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
            )
            session["username"] = user.username
            session["role_id"] = user.role
            if user_sub:
                session["subscription_tier_id"] = user_sub.subscription_tier_id
            else:
                session["subscription_tier_id"] = (
                    db_session.query(SubscriptionTiers)
                    .filter_by(tier="Free")
                    .first()
                    .id
                )
            session.permanent = True
            return dcc.Location(href="/account", id="login-redirect")
        else:
            return "Invalid username or password"


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
