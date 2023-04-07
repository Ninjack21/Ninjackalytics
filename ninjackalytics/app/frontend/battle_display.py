from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_uri
from poke_tool.poke_stats_gen_backend.models import *
from poke_tool.Backend.config import REPLAY_URL
import pandas as pd

engine = create_engine(db_uri)
Session = sessionmaker(engine)


class BattleData:
    def __init__(self, battle_id: str) -> None:
        self.battle_id = battle_id
        self.table_id = table_id

    def _get_table_id(self):
        """
        Use the battle_id to determine the table id
        """

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

    def _aggregate_player_info(self, player_number):
        damage_df = self.get_damage_info()
        damage_df = damage_df.rename(
            columns={
                "Source_Name": "Damage_Source",
                "Receiver": "Dmg_Receiver",
                "Type": "Dmg_Type",
            }
        )
        damage_df = damage_df[damage_df["Dealer"].str.startswith(f"P{player_number}")]

        healing_df = self.get_healing_info()
        healing_df = healing_df.rename(
            columns={
                "Source_Name": "Healing_Source",
                "Receiver": "Healing_Receiver",
                "Type": "Healing_Type",
            }
        )
        healing_df = healing_df[
            healing_df["Healing_Receiver"].str.startswith(f"P{player_number}")
        ]

        pivots_df = self.get_pivots_info()
        pivots_df = pivots_df.rename(
            columns={
                "Source_Name": "Pivot_Source",
            }
        )
        pivots_df = pivots_df[
            pivots_df["Pokemon_Enter"].str.startswith(f"P{player_number}")
        ]

        actions_df = self.get_actions_info()
        actions_df = actions_df[
            actions_df["Player_Number"].str.startswith(f"P{player_number}")
        ]

        df = (
            damage_df.merge(healing_df, how="outer", on=["Turn"])
            .merge(pivots_df, how="outer", on=["Turn"])
            .merge(actions_df, how="outer", on=["Turn"])
        )
        return df

    def get_aggregate_data(self):
        p1_df = self._aggregate_player_info(1)
        p2_df = self._aggregate_player_info(2)
        df = p1_df.merge(p2_df, how="outer", on=["Turn"])
        return df
