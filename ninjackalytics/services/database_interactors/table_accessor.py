import pandas as pd
from contextlib import contextmanager

from ninjackalytics.database import SessionLocal
from ninjackalytics.database.models.battles import (
    teams,
    battle_info,
    actions,
    damages,
    healing,
    pivots,
    errors,
)


class TableAccessor:
    def __init__(self):
        self.session = SessionLocal()

    def __del__(self):
        self.session.close()

    def get_teams(self):
        return pd.read_sql(self.session.query(teams).statement, self.session.bind)

    def get_battle_info(self):
        return pd.read_sql(self.session.query(battle_info).statement, self.session.bind)

    def get_actions(self):
        return pd.read_sql(self.session.query(actions).statement, self.session.bind)

    def get_damages(self):
        return pd.read_sql(self.session.query(damages).statement, self.session.bind)

    def get_healing(self):
        return pd.read_sql(self.session.query(healing).statement, self.session.bind)

    def get_pivots(self):
        return pd.read_sql(self.session.query(pivots).statement, self.session.bind)

    def get_errors(self):
        return pd.read_sql(self.session.query(errors).statement, self.session.bind)
