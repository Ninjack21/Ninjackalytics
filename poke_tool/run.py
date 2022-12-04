from frontend import create_app
from flask_sqlalchemy import SQLAlchemy
from config import db_design, db_uri
from sqlalchemy import create_engine


# create app and database object
app = create_app()
db = SQLAlchemy(app)
engine = create_engine(db_uri)

# initialize the database
from database import init_db, update_db

init_db()

# if we need to update - run the update function
if db_design == "update":
    update_db()


app.run(host="0.0.0.0", port=8080, debug=True)
