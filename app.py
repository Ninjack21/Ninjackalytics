import dash
import dash_bootstrap_components as dbc
from flask import Flask
from .config import SECRET_KEY

server = Flask(__name__)
server.secret_key = SECRET_KEY

# Initialize the Dash app with the existing Flask server
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# (Optional) Configure session lifetime or other Flask session settings
from datetime import timedelta

server.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    days=7
)  # Sessions last for 7 days

if __name__ == "__main__":
    app.run_server(debug=True)
