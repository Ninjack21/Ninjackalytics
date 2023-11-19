from ninjackalytics.database.database import Base, engine, SessionLocal
from ninjackalytics.database.models.battles import *
from ninjackalytics.database.models.metadata import *
import os

session = SessionLocal()

os.environ["FLASK_ENV"] = "testing"


def recreate_test_db():
    # Drop all tables in the database
    Base.metadata.drop_all(bind=engine)

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Commit the changes
    session.commit()

    # Close the connection
    session.close()
