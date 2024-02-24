from ninjackalytics.database.models import *
from sqlalchemy.orm import sessionmaker


def create_db(engine):
    print("Creating database...")
    # Create a session factory
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Commit the changes
    session.commit()
    print("Database created!")
    # Close the session
    session.close()
