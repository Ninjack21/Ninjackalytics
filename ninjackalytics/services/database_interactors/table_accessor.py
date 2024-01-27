import pandas as pd
from ninjackalytics.database import get_sessionlocal
from sqlalchemy.orm import sessionmaker
from ninjackalytics.database.models import *
from contextlib import contextmanager
from typing import Dict


@contextmanager
def session_scope(session):
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class TableAccessor:
    def __init__(self, *, engine: object = None):
        # prepare a session_maker either by the get_sessionlocal function (which handles engine creation
        # based on the FLASK_ENV environ) or by the engine passed in (which is used more manually)
        if engine is None:
            # store the database.py function which will utilize the FLASK_ENV environ
            self.session_maker = get_sessionlocal
        else:
            sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.session_maker = lambda: sessionlocal()

    def get_teams(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(teams).statement, session.bind)

    def get_battle_info(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(battle_info).statement, session.bind)

    def get_actions(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(actions).statement, session.bind)

    def get_damages(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(damages).statement, session.bind)

    def get_healing(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(healing).statement, session.bind)

    def get_pivots(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(pivots).statement, session.bind)

    def get_errors(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(errors).statement, session.bind)

    def get_pokemonmetadata(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(pokemonmetadata).statement, session.bind)

    def get_pvpmetadata(self):
        with session_scope(self.session_maker()) as session:
            return pd.read_sql(session.query(pvpmetadata).statement, session.bind)

    # TODO: fix this method - it does not work currently
    def _build_conditions(self, where_conditions: Dict):
        conditions = []
        for column_name, (operation, value) in where_conditions.items():
            conditions.append(getattr(getattr(self, column_name), operation)(value))
        
        return conditions