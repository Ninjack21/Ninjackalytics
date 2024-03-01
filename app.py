import dash
import dash_bootstrap_components as dbc
from flask import Flask, request, jsonify
from datetime import timedelta
from pages.config import SECRET_KEY, EMAIL_PASSWORD
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models.users import User
from flask_routes import init_flask_routes
from flask_mail import Mail

server = Flask(__name__)
server.secret_key = SECRET_KEY

# Flask-Mail configuration
server.config["MAIL_SERVER"] = "smtp.gmail.com"
server.config["MAIL_PORT"] = 587
server.config["MAIL_USE_TLS"] = True
server.config["MAIL_USERNAME"] = "ninjackalytics.application@gmail.com"
server.config["MAIL_PASSWORD"] = EMAIL_PASSWORD
server.config["MAIL_DEFAULT_SENDER"] = "ninjackalytics.application@gmail.com"

mail = Mail(server)  # Initialize Flask-Mail with your Flask server

init_flask_routes(server, mail)

# Initialize the Dash app with the existing Flask server
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)


server.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

if __name__ == "__main__":
    app.run_server(debug=True)
