from typing import Dict, List
import pandas as pd

from ninjackalytics.protocols.battle_parsing.protocols import BattleParser

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


class BattleDataRetriever:
    """
    A class used to retrieve battle data from a database.

    ...

    Attributes
    ----------
    session : sqlalchemy.orm.session.Session
        a session object to interact with the database

    Methods
    -------
    get_battle_info(battle_id: str) -> pd.DataFrame:
        Retrieves information about a specific battle from the database.

    get_teams(battle_id: str) -> pd.DataFrame:
        Retrieves information about the teams in a specific battle from the database.

    get_actions(battle_id: str) -> pd.DataFrame:
        Retrieves information about the actions taken in a specific battle from the database.

    get_damages(battle_id: str) -> pd.DataFrame:
        Retrieves information about the damages dealt in a specific battle from the database.

    get_healing(battle_id: str) -> pd.DataFrame:
        Retrieves information about the healing done in a specific battle from the database.

    get_pivots(battle_id: str) -> pd.DataFrame:
        Retrieves information about the pivots in a specific battle from the database.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BattleDataRetriever object.
        """
        self.session = SessionLocal()

    def get_battle_info(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the battle.
        """
        battle_info_db = (
            self.session.query(battle_info)
            .filter(battle_info.Battle_ID == battle_id)
            .first()
        )
        df = self._drop_unwanted_attrs(pd.DataFrame([battle_info_db.__dict__]))
        return df

    def get_teams(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about the teams in a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve team information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the teams in the battle.
        """
        team1_id = self.session.query(battle_info.P1_team).filter(
            battle_info.Battle_ID == battle_id
        )
        team2_id = self.session.query(battle_info.P2_team).filter(
            battle_info.Battle_ID == battle_id
        )

        team1 = self.session.query(teams).filter(teams.id == team1_id).first()
        team2 = self.session.query(teams).filter(teams.id == team2_id).first()
        battle_teams = [team1, team2]

        df = pd.DataFrame([team.__dict__ for team in battle_teams])
        return self._drop_unwanted_attrs(df)

    def get_actions(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about the actions taken in a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve action information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the actions taken in the battle.
        """
        dbid = self.get_db_id(battle_id)
        actions_db = self.session.query(actions).filter(actions.Battle_ID == dbid).all()
        df = pd.DataFrame([action.__dict__ for action in actions_db])
        return self._drop_unwanted_attrs(df)

    def get_damages(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about the damages dealt in a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve damage information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the damages dealt in the battle.
        """
        db_id = self.get_db_id(battle_id)
        damages_db = (
            self.session.query(damages).filter(damages.Battle_ID == db_id).all()
        )
        df = pd.DataFrame([damage.__dict__ for damage in damages_db])
        return self._drop_unwanted_attrs(df)

    def get_healing(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about the healing done in a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve healing information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the healing done in the battle.
        """
        db_id = self.get_db_id(battle_id)
        healing_db = (
            self.session.query(healing).filter(healing.Battle_ID == db_id).all()
        )
        df = pd.DataFrame([heal.__dict__ for heal in healing_db])
        return self._drop_unwanted_attrs(df)

    def get_pivots(self, battle_id: str) -> pd.DataFrame:
        """
        Retrieves information about the pivots in a specific battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve pivot information for.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing information about the pivots in the battle.
        """
        db_id = self.get_db_id(battle_id)
        pivots_db = self.session.query(pivots).filter(pivots.Battle_ID == db_id).all()
        df = pd.DataFrame([pivot.__dict__ for pivot in pivots_db])
        return self._drop_unwanted_attrs(df)

    def get_db_id(self, battle_id: str) -> int:
        """
        Retrieves the database ID of a battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve the database ID for.

        Returns
        -------
        int
            The database ID of the battle.
        """
        battle_info_db = (
            self.session.query(battle_info)
            .filter(battle_info.Battle_ID == battle_id)
            .first()
        )
        return battle_info_db.id

    def _drop_unwanted_attrs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drops unwanted attributes from a pandas DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The pandas DataFrame to drop unwanted attributes from.

        Returns
        -------
        pd.DataFrame
            The pandas DataFrame with unwanted attributes dropped.
        """
        # for some reason the instance state is still getting through
        unwanted_columns = ["FAIL", "_sa_instance_state"]
        for col in df.columns:
            if col in unwanted_columns:
                df.drop(columns=col)
        return df
