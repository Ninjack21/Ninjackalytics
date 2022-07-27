from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
import config


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='30zO8qGf2oLLH1&d@aE!',
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_uri
        
    if config.state == 'localhost': 
        from . import core
    else: 
        import core
    app.register_blueprint(core.bp)
    

    return app

app = create_app()


app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))