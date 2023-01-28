from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

import sys
import os


parent_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(1, parent_path)

from frontend import create_app
from config import db_uri

# create app and database object
app = create_app()
db = SQLAlchemy(app)
engine = create_engine(db_uri)


app.run(host="0.0.0.0", port=8080, debug=True)
