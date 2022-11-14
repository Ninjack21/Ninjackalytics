from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_uri
from ..poke_stats_gen_backend.models import *
from ..Backend.config import REPLAY_URL
import pandas as pd

engine = create_engine(db_uri)
Session = sessionmaker(engine)


class BattleData:
    def __init__(self, url: str) -> None:
        self.url = url
        self.battle_id = url.split(REPLAY_URL)[1]

    def get_basic_info(self):
        with Session.begin() as session:
            q = (
                session.query(battle_info)
                .with_entities(
                    battle_info.Battle_ID,
                    battle_info.Format,
                    battle_info.P1,
                    battle_info.P2,
                    battle_info.Rank,
                    battle_info.Winner,
                )
                .filter_by(Battle_ID=self.battle_id)
            ).statement
            df = pd.read_sql(q, session.bind)
        return df

    def get_damage_info(self):
        with Session.begin() as session:
            q = (
                session.query(damages)
                .with_entities(
                    damages.Damage,
                    damages.Dealer,
                    damages.Receiver,
                    damages.Source_Name,
                    damages.Turn,
                    damages.Type,
                )
                .filter_by(Battle_ID=self.battle_id)
            ).statement
            df = pd.read_sql(q, session.bind)
        return df

    def get_healing_info(self):
        with Session.begin() as session:
            q = (
                session.query(healing)
                .with_entities(
                    healing.Healing,
                    healing.Receiver,
                    healing.Source_Name,
                    healing.Turn,
                    healing.Type,
                )
                .filter_by(Battle_ID=self.battle_id)
            ).statement
            df = pd.read_sql(q, session.bind)
        return df

    def get_pivots_info(self):
        with Session.begin() as session:
            q = (
                session.query(pivots)
                .with_entities(pivots.Pokemon_Enter, pivots.Source_Name, pivots.Turn)
                .filter_by(Battle_ID=self.battle_id)
            ).statement
            df = pd.read_sql(q, session.bind)
        return df

    def get_actions_info(self):
        with Session.begin() as session:
            q = (
                session.query(actions)
                .with_entities(
                    actions.Action,
                    actions.Turn,
                    actions.Player_Number,
                )
                .filter_by(Battle_ID=self.battle_id)
            ).statement
            df = pd.read_sql(q, session.bind)
        return df

    def get_aggregate_info(self):
        damage_df = self.get_damage_info()
        healing_df = self.get_healing_info()
        pivots_df = self.get_pivots_info()
        actions_df = self.get_actions_info()

        df = (
            damage_df.merge(healing_df, how="outer", on=["Turn"])
            .merge(pivots_df, how="outer", on=["Turn"])
            .merge(actions_df, how="outer", on=["Turn"])
        )
        return df
