from ninjackalytics.database.database import Base, get_engine, get_sessionlocal
from ninjackalytics.database.models import *
import os

session = get_sessionlocal()

os.environ["FLASK_ENV"] = "testing"


def create_new_tables():
    # Create all tables in the database
    Base.metadata.create_all(bind=get_engine())

    # Commit the changes
    session.commit()

    # Close the connection
    session.close()
