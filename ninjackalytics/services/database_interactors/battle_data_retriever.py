from typing import Dict, List
import pandas as pd
from contextlib import contextmanager

from ninjackalytics.protocols.battle_parsing.protocols import BattleParser

from ninjackalytics.database import get_sessionlocal
from ninjackalytics.database.models.battles import (
    teams,
    battle_info,
    actions,
    damages,
    healing,
    pivots,
    errors,
)


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
        pass

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
        with session_scope() as session:
            battle_info_db = (
                session.query(battle_info)
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
        with session_scope() as session:
            team1_id = session.query(battle_info.P1_team).filter(
                battle_info.Battle_ID == battle_id
            )
            team2_id = session.query(battle_info.P2_team).filter(
                battle_info.Battle_ID == battle_id
            )

            team1 = session.query(teams).filter(teams.id == team1_id).first()
            team2 = session.query(teams).filter(teams.id == team2_id).first()
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
        with session_scope() as session:
            dbid = self.get_db_id(battle_id)
            actions_db = session.query(actions).filter(actions.Battle_ID == dbid).all()
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
        with session_scope() as session:
            db_id = self.get_db_id(battle_id)
            damages_db = session.query(damages).filter(damages.Battle_ID == db_id).all()
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
        with session_scope() as session:
            db_id = self.get_db_id(battle_id)
            healing_db = session.query(healing).filter(healing.Battle_ID == db_id).all()
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
        with session_scope() as session:
            db_id = self.get_db_id(battle_id)
            pivots_db = session.query(pivots).filter(pivots.Battle_ID == db_id).all()
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
        with session_scope() as session:
            battle_info_db = (
                session.query(battle_info)
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

    # TODO: ADD UNIT TESTS FOR ALL METHODS BELOW
    def get_battle_data(self, battle_id: str) -> Dict[str, pd.DataFrame]:
        """
        Retrieves all data about a battle from the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to retrieve data for.

        Returns
        -------
        Dict[str, pd.DataFrame]
            A dictionary containing all data about the battle.
        """
        battle_data = {}
        battle_data["battle_info"] = self.get_battle_info(battle_id)
        battle_data["teams"] = self.get_teams(battle_id)
        battle_data["actions"] = self.get_actions(battle_id)
        battle_data["damages"] = self.get_damages(battle_id)
        battle_data["healing"] = self.get_healing(battle_id)
        battle_data["pivots"] = self.get_pivots(battle_id)
        return battle_data

    def check_if_battle_exists(self, battle_id: str) -> bool:
        """
        Checks if a battle exists in the database.

        Parameters
        ----------
        battle_id : int
            The ID of the battle to check for.

        Returns
        -------
        bool
            True if the battle exists in the database, False otherwise.
        """
        with session_scope() as session:
            battle_info_db = (
                session.query(battle_info)
                .filter(battle_info.Battle_ID == battle_id)
                .first()
            )
            if battle_info_db:
                return True
            return False
