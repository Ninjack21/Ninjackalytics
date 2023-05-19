import unittest
from unittest.mock import Mock
from datetime import datetime
import os

os.environ["FLASK_ENV"] = "testing"

from app.config import TestingConfig
from app.database import Base, engine, SessionLocal
from app.services.database_interactors.battle_data_uploader import BattleDataUploader
from app.models.battles import (
    teams,
    battle_info,
    actions,
    damages,
    healing,
    pivots,
    errors,
)


class TestBattleDataUploader(unittest.TestCase):
    def setUp(self):
        self.session = SessionLocal()
        self.battle_data_uploader = BattleDataUploader()

        # create all tables in the test database
        Base.metadata.create_all(bind=engine)

        teams = [{"Pok1": "Pikachu"}, {"Pok1": "Charizard"}]
        general_info = {
            "Format": "gen8randombattle",
            "Date_Submitted": datetime(year=2023, month=1, day=1),
            "P1": "Player1",
            "P2": "Player2",
            "Winner": "Player1",
            "Rank": 1500,
        }
        actions = [
            {"Turn": 1, "Action": "switch", "Player_Number": 1},
            {"Turn": 1, "Action": "switch", "Player_Number": 2},
        ]
        damages = [
            {
                "Damage": 10,
                "Dealer": "Pikachu",
                "Dealer_Player_Number": 1,
                "Source_Name": "Thunderbolt",
                "Receiver": "Charizard",
                "Receiver_Player_Number": 2,
                "Turn": 1,
                "Type": "move",
            },
        ]
        healing = [
            {
                "Healing": 10,
                "Receiver": "Pikachu",
                "Receiver_Player_Number": 1,
                "Source_Name": "Recover",
                "Turn": 1,
                "Type": "move",
            }
        ]

        pivots = [
            {
                "Pokemon_Enter": "Pikachu",
                "Player_Number": 1,
                "Turn": 1,
                "Source_Name": "action",
            }
        ]

        MockParser = Mock()
        MockParser.teams = teams
        MockParser.general_info = general_info
        MockParser.actions = actions
        MockParser.damages = damages
        MockParser.healing = healing
        MockParser.pivots = pivots
        self.mock_parser = MockParser

    def tearDown(self):
        # drop all tables in the test database
        Base.metadata.drop_all(bind=engine)

    def test_teams_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that the teams were uploaded correctly
        team1 = (self.session.query(teams).filter(teams.Pok1 == "Pikachu")).first()
        self.assertEqual(team1.Pok1, "Pikachu")
        team2 = self.session.query(teams).filter(teams.Pok1 == "Charizard").first()
        self.assertEqual(team2.Pok1, "Charizard")

    def test_teams_alphabetizes(self):
        # the first team should end up re-ordered such that Abra appears in Pok1
        self.mock_parser.teams = [
            {"Pok1": "Charizard", "Pok2": "Abra"},
            {"Pok1": "Pikachu"},
        ]
        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that Abra appears as Pok1 and then Charizard as Pok2
        team1 = (self.session.query(teams).filter(teams.id == 1)).first()
        self.assertEqual(team1.Pok1, "Abra")
        self.assertEqual(team1.Pok2, "Charizard")

    def test_general_info_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        battle = (
            self.session.query(battle_info)
            .filter(battle_info.P1 == "Player1")
            .filter(battle_info.P2 == "Player2")
            .first()
        )
        self.assertEqual(battle.P1, "Player1")
        self.assertEqual(battle.P2, "Player2")
        self.assertEqual(battle.Winner, "Player1")
        self.assertEqual(battle.P1_team, 1)
        self.assertEqual(battle.P2_team, 2)
        self.assertEqual(battle.Rank, 1500)

    def test_actions_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        action1 = (
            self.session.query(actions)
            .filter(actions.Turn == 1)
            .filter(actions.Action == "switch")
            .filter(actions.Player_Number == 1)
            .first()
        )
        self.assertEqual(action1.Turn, 1)
        self.assertEqual(action1.Action, "switch")
        self.assertEqual(action1.Player_Number, 1)
        action2 = (
            self.session.query(actions)
            .filter(actions.Turn == 1)
            .filter(actions.Action == "switch")
            .filter(actions.Player_Number == 2)
            .first()
        )
        self.assertEqual(action2.Turn, 1)
        self.assertEqual(action2.Action, "switch")
        self.assertEqual(action2.Player_Number, 2)

    def test_damages_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_damages = (self.session.query(damages)).all()

        self.assertEqual(len(query_damages), 1)
        self.assertEqual(query_damages[0].Damage, 10)
        self.assertEqual(query_damages[0].Dealer, "Pikachu")
        self.assertEqual(query_damages[0].Dealer_Player_Number, 1)
        self.assertEqual(query_damages[0].Source_Name, "Thunderbolt")
        self.assertEqual(query_damages[0].Receiver, "Charizard")
        self.assertEqual(query_damages[0].Receiver_Player_Number, 2)
        self.assertEqual(query_damages[0].Turn, 1)
        self.assertEqual(query_damages[0].Type, "move")

    def test_healing_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_healing = (self.session.query(healing)).all()

        self.assertEqual(len(query_healing), 1)
        self.assertEqual(query_healing[0].Healing, 10)
        self.assertEqual(query_healing[0].Receiver, "Pikachu")
        self.assertEqual(query_healing[0].Receiver_Player_Number, 1)
        self.assertEqual(query_healing[0].Source_Name, "Recover")
        self.assertEqual(query_healing[0].Turn, 1)
        self.assertEqual(query_healing[0].Type, "move")

    def test_pivots_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_pivots = (self.session.query(pivots)).all()

        self.assertEqual(len(query_pivots), 1)
        self.assertEqual(query_pivots[0].Pokemon_Enter, "Pikachu")
        self.assertEqual(query_pivots[0].Player_Number, 1)
        self.assertEqual(query_pivots[0].Turn, 1)
        self.assertEqual(query_pivots[0].Source_Name, "action")


if __name__ == "__main__":
    unittest.main()
