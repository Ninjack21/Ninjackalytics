import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)
from ninjackalytics.database.database import Base, get_engine, get_sessionlocal
from ninjackalytics.database.models.battles import *
from ninjackalytics.database.models.metadata import *

session = get_sessionlocal()

if "production" not in os.environ.get("FLASK_ENV"):
    # Drop all tables in the database
    Base.metadata.drop_all(bind=get_engine())

    # Create all tables in the database
    Base.metadata.create_all(bind=get_engine())

    # Commit the changes
    session.commit()

    # Close the connection
    session.close()

else:
    raise Exception("You are not allowed to run this script in production")
