import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)


from ninjackalytics.database.database import Base, get_engine, get_sessionlocal
from ninjackalytics.database.models import *

session = get_sessionlocal()


def create_new_tables():
    # Create all tables in the database
    Base.metadata.create_all(bind=get_engine())

    # Commit the changes
    session.commit()

    # Close the connection
    session.close()


if __name__ == "__main__":
    create_new_tables()
