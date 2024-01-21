import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from sqlalchemy.orm import make_transient
from ninjackalytics.database.config import OldProductionConfig, NewProductionConfig
from tqdm import tqdm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models import *


# Function to create a database engine
def create_db_engine(config):
    db_uri = config.SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_uri)
    return engine


def create_tables(engine):
    Base.metadata.create_all(bind=engine)


# Function to create a session local
def create_session_local(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# Create engines
old_db_engine = create_db_engine(OldProductionConfig)
new_db_engine = create_db_engine(NewProductionConfig)

# Create session locals
old_db_session_local = create_session_local(old_db_engine)
new_db_session_local = create_session_local(new_db_engine)


def migrate_data(old_session, new_session, model, batch_size=50000):
    offset = 0
    while True:
        old_data = old_session.query(model).limit(batch_size).offset(offset).all()
        if not old_data:
            break
        for record in tqdm(old_data, f"Migrating {model.__tablename__}"):
            make_transient(record)
            record.id = None  # Reset primary key
            new_session.add(record)
        new_session.commit()  # Commit in batches
        offset += batch_size


# Main migration function
def main_migration():
    print("create new db")
    # Create new database engine for NewProductionConfig
    new_db_engine = create_db_engine(NewProductionConfig)
    # Create tables in the new database
    create_tables(new_db_engine)

    print("prepare sessionlocals for old and new db")

    # Create session locals for old and new databases
    old_db_engine = create_db_engine(OldProductionConfig)
    old_db_session_local = create_session_local(old_db_engine)
    new_db_session_local = create_session_local(new_db_engine)

    old_session = old_db_session_local()
    new_session = new_db_session_local()

    try:
        print("migrate data")
        # Migrate data for each table
        migrate_data(old_session, new_session, teams)
        migrate_data(old_session, new_session, battle_info)
        migrate_data(old_session, new_session, actions)
        migrate_data(old_session, new_session, damages)
        migrate_data(old_session, new_session, healing)
        migrate_data(old_session, new_session, pivots)
        migrate_data(old_session, new_session, errors)
        migrate_data(old_session, new_session, pokemonmetadata)
        migrate_data(old_session, new_session, pvpmetadata)
        # ... repeat for other tables ...

        new_session.commit()  # Commit changes
    except Exception as e:
        print(f"An error occurred: {e}")
        new_session.rollback()  # Rollback changes on error
    finally:
        old_session.close()
        new_session.close()


if __name__ == "__main__":
    main_migration()
