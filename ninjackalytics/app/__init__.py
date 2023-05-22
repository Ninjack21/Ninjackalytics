import os

from flask import Flask

import os

from flask import Flask
from .config import DevelopmentConfig, TestingConfig, ProductionConfig


def create_app(config_name=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # load the default configuration
    app.config.from_object(DevelopmentConfig)

    # override the default configuration with the specified configuration
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    elif config_name == "production":
        app.config.from_object(ProductionConfig)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import database

    database.init_app(app)

    return app
