# Assuming this is in a file named login.py in your 'pages' directory
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from werkzeug.security import check_password_hash
from ninjackalytics.database.models import User
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/login")


def layout():
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
                                id="login-username", type="text", placeholder="Username"
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
            html.Span(id="login-output", className="mt-3", style={"color": "white"}),
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
)
def login(n_clicks, username, password):
    if n_clicks is None or n_clicks < 1:
        return no_update
    with get_sessionlocal() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.hashed_password, password):
            # Here you would handle successful login, e.g., by setting session data
            return "Login successful"
        else:
            return "Invalid username or password"
