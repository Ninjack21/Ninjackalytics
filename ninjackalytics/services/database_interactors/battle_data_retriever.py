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
    get_battle_info(battle_id: int) -> pd.DataFrame:
        Retrieves information about a specific battle from the database.

    get_teams(battle_id: int) -> pd.DataFrame:
        Retrieves information about the teams in a specific battle from the database.

    get_actions(battle_id: int) -> pd.DataFrame:
        Retrieves information about the actions taken in a specific battle from the database.

    get_damages(battle_id: int) -> pd.DataFrame:
        Retrieves information about the damages dealt in a specific battle from the database.

    get_healing(battle_id: int) -> pd.DataFrame:
        Retrieves information about the healing done in a specific battle from the database.

    get_pivots(battle_id: int) -> pd.DataFrame:
        Retrieves information about the pivots in a specific battle from the database.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BattleDataRetriever object.
        """
        self.session = SessionLocal()

    def get_battle_info(self, battle_id: int) -> pd.DataFrame:
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
        print(f"\n\n\n{battle_info_db}\n\n\n")
        return pd.DataFrame([battle_info_db.__dict__])

    def get_teams(self, battle_id: int) -> pd.DataFrame:
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
        teams_db = self.session.query(teams).filter(teams.Battle_ID == battle_id).all()
        return pd.DataFrame([team.__dict__ for team in teams_db])

    def get_actions(self, battle_id: int) -> pd.DataFrame:
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
        actions_db = (
            self.session.query(actions).filter(actions.Battle_ID == battle_id).all()
        )
        return pd.DataFrame([action.__dict__ for action in actions_db])

    def get_damages(self, battle_id: int) -> pd.DataFrame:
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
        damages_db = (
            self.session.query(damages).filter(damages.Battle_ID == battle_id).all()
        )
        return pd.DataFrame([damage.__dict__ for damage in damages_db])

    def get_healing(self, battle_id: int) -> pd.DataFrame:
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
        healing_db = (
            self.session.query(healing).filter(healing.Battle_ID == battle_id).all()
        )
        return pd.DataFrame([heal.__dict__ for heal in healing_db])

    def get_pivots(self, battle_id: int) -> pd.DataFrame:
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
        pivots_db = (
            self.session.query(pivots).filter(pivots.Battle_ID == battle_id).all()
        )
        return pd.DataFrame([pivot.__dict__ for pivot in pivots_db])
