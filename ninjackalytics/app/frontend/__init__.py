from flask import Flask, render_template
import sys
import os


parent_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(1, parent_path)

from config import db_uri
from .app import create_dash_application


def create_app(test_config=None, db_uri=db_uri):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False, SQLALCHEMY_DATABASE_URI=db_uri
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/")
    def home_page():
        return render_template("user_navigation/submit.html")

    create_dash_application(app)

    return app
