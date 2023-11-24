import pandas as pd
from ninjackalytics.database import get_sessionlocal
from ninjackalytics.database.models import *
from contextlib import contextmanager


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_sessionlocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class TableAccessor:
    def __init__(self):
        pass

    def get_teams(self):
        with session_scope() as session:
            return pd.read_sql(session.query(teams).statement, session.bind)

    def get_battle_info(self):
        with session_scope() as session:
            return pd.read_sql(session.query(battle_info).statement, session.bind)

    def get_actions(self):
        with session_scope() as session:
            return pd.read_sql(session.query(actions).statement, session.bind)

    def get_damages(self):
        with session_scope() as session:
            return pd.read_sql(session.query(damages).statement, session.bind)

    def get_healing(self):
        with session_scope() as session:
            return pd.read_sql(session.query(healing).statement, session.bind)

    def get_pivots(self):
        with session_scope() as session:
            return pd.read_sql(session.query(pivots).statement, session.bind)

    def get_errors(self):
        with session_scope() as session:
            return pd.read_sql(session.query(errors).statement, session.bind)

    def get_pokemonmetadata(self):
        with session_scope() as session:
            return pd.read_sql(session.query(pokemonmetadata).statement, session.bind)

    def get_pvpmetadata(self):
        with session_scope() as session:
            return pd.read_sql(session.query(pvpmetadata).statement, session.bind)
