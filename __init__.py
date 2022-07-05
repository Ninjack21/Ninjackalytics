from flask import Flask 
import logging
import sys
import os

logging.basicConfig(filename = 'apperrors.log', level = logging.ERROR, 
                format = '%(asctime)s:%(funcName)s')

dir_path = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(dir_path, "templates")

def create_app():
    # create and configure the app
    app = Flask(__name__, template_folder=template_dir)
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
app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logging.StreamHandler(sys.stdout))