from typing import Dict, List
from contextlib import contextmanager

from ninjackalytics.protocols.battle_parsing.protocols import BattleParser

from ninjackalytics.database import SessionLocal
from ninjackalytics.database.models.battles import (
    teams,
    battle_info,
    actions,
    damages,
    healing,
    pivots,
)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class BattleDataUploader:
    """
    A class used to upload battle data to the database

    Attributes
    ----------
    session : SessionLocal
        a SQLAlchemy session object
    p1_team_id : int
        the id of player 1's team in the database
    p2_team_id : int
        the id of player 2's team in the database
    battle_id : int
        the id of the battle in the database

    Methods
    -------
    close_session() -> None:
        Closes the SQLAlchemy session
    _upload_teams(teams_list: List[List[object]]) -> int:
        Uploads the teams to the database and returns the id of player 2's team

        Parameters
        ----------
        teams_list : List[List[object]]
            A list of two lists, each containing the Pokemon objects for each player's team

        Returns
        -------
        int
            The id of player 2's team in the database
    _upload_general_info(general_info: Dict[str, str]) -> int:
        Uploads the general battle info to the database and returns the battle's id

        Parameters
        ----------
        general_info : Dict[str, str]
            A dictionary containing the general battle information

        Returns
        -------
        int
            The id of the battle in the database
    _upload_actions(actions_list: List[Dict[str, str]]) -> None:
        Uploads the actions to the database

        Parameters
        ----------
        actions_list : List[Dict[str, str]]
            A list of dictionaries containing the action information
    _upload_damages(damages_list: List[Dict[str, str]]) -> None:
        Uploads the damages to the database

        Parameters
        ----------
        damages_list : List[Dict[str, str]]
            A list of dictionaries containing the damage information
    _upload_healing(healing_list: List[Dict[str, str]]) -> None:
        Uploads the healing to the database

        Parameters
        ----------
        healing_list : List[Dict[str, str]]
            A list of dictionaries containing the healing information
    _upload_pivots(pivots_list: List[Dict[str, str]]) -> None:
        Uploads the pivots to the database

        Parameters
        ----------
        pivots_list : List[Dict[str, str]]
            A list of dictionaries containing the pivot information
    upload_battle(parser: BattleParser) -> None:
        Uploads the data from the BattleParser to the database

        Parameters
        ----------
        parser : BattleParser
            An instance of the BattleParser class containing the battle data
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BattleDataUploader object.
        """
        self.p1_team_id = None
        self.p2_team_id = None
        self.battle_id = None

    def _upload_teams(self, teams_list: List[List[object]]) -> int:
        """
        Uploads the teams to the database and returns the id of player 2's team

        Parameters
        ----------
        teams_list : List[List[object]]
            A list of two lists, each containing the Pokemon objects for each player's team

        Returns
        -------
        int
            The id of player 2's team in the database
        """
        with session_scope() as session:
            for pnum, team in enumerate(teams_list):
                mon_names = [mon.real_name for mon in team.pokemon]
                mon_names.sort()
                # create the team dictionary
                team_dict = {}
                for i, mon in enumerate(mon_names):
                    team_dict[f"Pok{i+1}"] = mon

                team_db = teams(**team_dict)
                session.add(team_db)
                session.commit()
                session.refresh(team_db)
                if pnum == 0:
                    self.p1_team_id = team_db.id
                else:
                    self.p2_team_id = team_db.id
            return self.p2_team_id

    def _check_if_battle_exists(self, general_info: Dict[str, str]) -> bool:
        """
        Checks if the battle already exists in the database

        Parameters
        ----------
        general_info : Dict[str, str]
            A dictionary containing the general battle information

        Returns
        -------
        bool
            True if the battle exists, False otherwise
        """
        with session_scope() as session:
            existing_battle = (
                session.query(battle_info)
                .filter(battle_info.Battle_ID == general_info["Battle_ID"])
                .first()
            )
            if existing_battle:
                # set the battle_id
                self.battle_id = existing_battle.Battle_ID
                return True
            return False

    def _upload_general_info(self, general_info: Dict[str, str]) -> int:
        """
        Uploads the general battle info to the database and returns the battle's id

        Parameters
        ----------
        general_info : Dict[str, str]
            A dictionary containing the general battle information

        Returns
        -------
        int
            The id of the battle in the database
        """
        with session_scope() as session:
            general_info["P1_team"] = self.p1_team_id
            general_info["P2_team"] = self.p2_team_id
            battle_info_db = battle_info(**general_info)
            session.add(battle_info_db)
            session.commit()
            session.refresh(battle_info_db)
            self.battle_id = battle_info_db.id
            return self.battle_id

    def _upload_actions(self, actions_list: List[Dict[str, str]]) -> None:
        """
        Uploads the actions to the database

        Parameters
        ----------
        actions_list : List[Dict[str, str]]
            A list of dictionaries containing the action information
        """
        with session_scope() as session:
            for action in actions_list:
                action["Battle_ID"] = self.battle_id
                action_db = actions(**action)
                session.add(action_db)
            session.commit()

    def _upload_damages(self, damages_list: List[Dict[str, str]]) -> None:
        """
        Uploads the damages to the database

        Parameters
        ----------
        damages_list : List[Dict[str, str]]
            A list of dictionaries containing the damage information
        """
        with session_scope() as session:
            for damage in damages_list:
                damage["Battle_ID"] = self.battle_id
                damage_db = damages(**damage)
                session.add(damage_db)
            session.commit()

    def _upload_healing(self, healing_list: List[Dict[str, str]]) -> None:
        """
        Uploads the healing to the database

        Parameters
        ----------
        healing_list : List[Dict[str, str]]
            A list of dictionaries containing the healing information
        """
        with session_scope() as session:
            for heal in healing_list:
                heal["Battle_ID"] = self.battle_id
                heal_db = healing(**heal)
                session.add(heal_db)
            session.commit()

    def _upload_pivots(self, pivots_list: List[Dict[str, str]]) -> None:
        """
        Uploads the pivots to the database

        Parameters
        ----------
        pivots_list : List[Dict[str, str]]
            A list of dictionaries containing the pivot information
        """
        with session_scope() as session:
            for pivot in pivots_list:
                pivot["Battle_ID"] = self.battle_id
                pivot_db = pivots(**pivot)
                session.add(pivot_db)
            session.commit()

    def upload_battle(self, parser: BattleParser) -> None:
        """
        Uploads the data from the BattleParser to the database

        Parameters
        ----------
        parser : BattleParser
            An instance of the BattleParser class containing the battle data
        """
        exists = self._check_if_battle_exists(parser.general_info)
        if not exists:
            self._upload_teams(parser.teams)
            self._upload_general_info(parser.general_info)
            self._upload_actions(parser.action_info)
            self._upload_damages(parser.damages_info)
            self._upload_healing(parser.heals_info)
            self._upload_pivots(parser.pivot_info)
