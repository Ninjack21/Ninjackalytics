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

    def get_teams(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(teams)

            if conditions:
                query = self._add_conditions(query, conditions)

            return pd.read_sql(query.statement, session.bind)

    def get_battle_info(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(battle_info)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(battle_info).statement, session.bind)

    def get_actions(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(actions)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(actions).statement, session.bind)

    def get_damages(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(damages)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(damages).statement, session.bind)

    def get_healing(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(healing)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(healing).statement, session.bind)

    def get_pivots(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(pivots)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(pivots).statement, session.bind)

    def get_errors(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(errors)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(errors).statement, session.bind)

    def get_pokemonmetadata(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(pokemonmetadata)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(pokemonmetadata).statement, session.bind)

    def get_pvpmetadata(self, conditions: Dict = None):
        with session_scope(self.session_maker()) as session:
            query = session.query(pvpmetadata)

            if conditions:
                query = self._add_conditions(query, conditions)
            return pd.read_sql(session.query(pvpmetadata).statement, session.bind)

    def _add_conditions(self, query, conditions: Dict):
        """
        conditions_format = {
            'column_name': {'op': '>=', 'value': 100},
            'another_column': {'op': 'like', 'value': '%pattern%'},
        }
        """
        # Map operation strings to SQLAlchemy functions
        op_map = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            "<=": lambda f, v: f <= v,
            ">": lambda f, v: f > v,
            ">=": lambda f, v: f >= v,
            "like": lambda f, v: f.like(v),
            "in": lambda f, v: f.in_(v),
            # Add more operations as needed
        }

        for column, cond in conditions.items():
            operation = cond["op"]
            value = cond["value"]

            # Retrieve the column attribute
            field = getattr(
                teams, column
            )  # Assuming 'teams' is the model, adjust as necessary

            # Apply the condition
            if operation in op_map:
                query = query.filter(op_map[operation](field, value))
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        return query
