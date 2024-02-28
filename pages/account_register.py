from flask import session
import dash
from dash import html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from werkzeug.security import generate_password_hash
from ninjackalytics.database.models import (
    User,
    Roles,
    SubscriptionTiers,
)
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/register")


def layout():
    return dbc.Container(
        [
            navbar(),
            html.H1("Register", style={"color": "white"}),
            # username input
            dbc.Row(  # Use Row for structuring the layout
                [
                    dbc.Col(
                        [
                            dbc.Label("Username", style={"color": "white"}),
                            dbc.Input(
                                id="register-username",
                                type="text",
                                placeholder="Username",
                            ),
                        ],
                        width=4,  # Adjust the width as needed
                    ),
                ]
            ),
            # password input
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Password", style={"color": "white"}),
                            dbc.Input(
                                id="register-password",
                                type="password",
                                placeholder="Password",
                            ),
                        ],
                        width=4,  # Adjust the width as needed
                    ),
                ]
            ),
            # email input
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Email", style={"color": "white"}),
                            dbc.Input(
                                id="register-email",
                                type="text",
                                placeholder="email",
                            ),
                        ],
                        width=4,  # Adjust the width as needed
                    ),
                ]
            ),
            dbc.Button(
                "Create Account", id="register-button", className="mt-3"
            ),  # Added mt-3 for margin-top
            html.Span(
                id="register-output", className="mt-3", style={"color": "white"}
            ),  # Added mt-3 for margin-top
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
    Output("register-output", "children"),
    Input("register-button", "n_clicks"),
    [
        State("register-username", "value"),
        State("register-password", "value"),
        State("register-email", "value"),
    ],
)
def register(n_clicks, username, password, email):
    if n_clicks is None or n_clicks < 1:
        return no_update
    with get_sessionlocal() as session:
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return "Username already exists"
        hashed_password = generate_password_hash(password)
        # check that the email is not already in use
        existing_email = session.query(User).filter_by(email=email).first()
        if existing_email:
            return "Email already in use"

        # default subscription tier is Free and role is User
        # get the default sub tier id and default role id
        sub_id = session.query(SubscriptionTiers).filter_by(tier="Free").first()
        role_id = session.query(Roles).filter_by(role="User").first()

        new_user = User(
            username=username,
            hashed_password=hashed_password,
            email=email,
            subscription_tier=sub_id.id,
            role=role_id.id,
        )
        session.add(new_user)
        session.commit()
        return "Account created successfully"
