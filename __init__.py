from flask import Flask 
import logging
import sys
import os

logging.basicConfig(filename = 'apperrors.log', level = logging.ERROR, 
                format = '%(asctime)s:%(funcName)s')



def create_app():
    # create and configure the app
    templates_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, template_folder = templates_folder)
    app.config.from_mapping(
        SECRET_KEY='30zO8qGf2oLLH1&d@aE!',
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)
        
    import core
    app.register_blueprint(core.bp)

    return app

app = create_app()
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))