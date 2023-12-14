import unittest
from unittest.mock import Mock
from datetime import datetime
import os

os.environ["FLASK_ENV"] = "testing"

from ninjackalytics.database.config import TestingConfig
from ninjackalytics.database import Base, get_engine, get_sessionlocal
from ninjackalytics.services.database_interactors.battle_data_uploader import (
    BattleDataUploader,
    session_scope,
)
from ninjackalytics.services.battle_parsing import BattleParser
from ninjackalytics.services.battle_parsing.battle_data.battle_pokemon import (
    BattlePokemon,
)
from ninjackalytics.database.models.battles import (
    teams,
    battle_info,
    actions,
    damages,
    healing,
    pivots,
    errors,
)

from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)


class TestBattleDataUploader(unittest.TestCase):
    def setUp(self):
        self.session = get_sessionlocal()
        self.battle_data_uploader = BattleDataUploader()

        # create all tables in the test database
        Base.metadata.create_all(bind=get_engine())

        battle = TestBattle()
        battle_pokemon = BattlePokemon(battle)
        battle_parser = BattleParser(battle, battle_pokemon)
        battle_parser.analyze_battle()

        self.mock_parser = battle_parser

    def tearDown(self):
        # drop all tables in the test database
        Base.metadata.drop_all(bind=get_engine())

    def test_teams_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that the teams were uploaded correctly
        team1 = (self.session.query(teams).filter(teams.Pok1 == "Azumarill")).first()
        self.assertEqual(team1.Pok1, "Azumarill")
        team2 = self.session.query(teams).filter(teams.Pok1 == "Corviknight").first()
        self.assertEqual(team2.Pok1, "Corviknight")

    def test_teams_alphabetizes(self):
        """
        |poke|p1|Azumarill, M|
        |poke|p1|Great Tusk|
        |poke|p1|Iron Valiant|
        |poke|p1|Sneasler, M|
        |poke|p1|Garganacl, M|
        |poke|p1|Ogerpon-Wellspring, F|
        |poke|p2|Gliscor, M|
        |poke|p2|Corviknight, M|
        |poke|p2|Kingambit, F|
        |poke|p2|Iron Valiant|
        |poke|p2|Slowking-Galar, F|
        |poke|p2|Great Tusk|
        """

        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that the above were appropriately alphabetized into the db
        team1 = (self.session.query(teams).filter(teams.id == 1)).first()
        self.assertEqual(team1.Pok1, "Azumarill")
        self.assertEqual(team1.Pok2, "Garganacl")
        self.assertEqual(team1.Pok3, "Great Tusk")
        self.assertEqual(team1.Pok4, "Iron Valiant")
        self.assertEqual(team1.Pok5, "Ogerpon-Wellspring")
        self.assertEqual(team1.Pok6, "Sneasler")

        team2 = (self.session.query(teams).filter(teams.id == 2)).first()
        self.assertEqual(team2.Pok1, "Corviknight")
        self.assertEqual(team2.Pok2, "Gliscor")
        self.assertEqual(team2.Pok3, "Great Tusk")
        self.assertEqual(team2.Pok4, "Iron Valiant")
        self.assertEqual(team2.Pok5, "Kingambit")
        self.assertEqual(team2.Pok6, "Slowking-Galar")

    def test_general_info_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        battle = (
            self.session.query(battle_info)
            .filter(battle_info.P1 == "massivesket")
            .filter(battle_info.P2 == "Buzzma")
            .first()
        )
        self.assertEqual(battle.P1, "massivesket")
        self.assertEqual(battle.P2, "Buzzma")
        self.assertEqual(battle.Winner, "massivesket")
        self.assertEqual(battle.P1_team, 1)
        self.assertEqual(battle.P2_team, 2)
        self.assertEqual(battle.Rank, 1337)

    def test_actions_uploaded(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        action1 = (
            self.session.query(actions)
            .filter(actions.Turn == 0)
            .filter(actions.Player_Number == 1)
            .first()
        )
        self.assertEqual(action1.Turn, 0)
        self.assertEqual(action1.Action, "switch")
        self.assertEqual(action1.Player_Number, 1)
        action2 = (
            self.session.query(actions)
            .filter(actions.Turn == 0)
            .filter(actions.Player_Number == 2)
            .first()
        )
        self.assertEqual(action2.Turn, 0)
        self.assertEqual(action2.Action, "switch")
        self.assertEqual(action2.Player_Number, 2)

    def test_damages_uploaded(self):
        """
        |t:|1697406815
        |start
        |switch|p1a: Femboy IX|Azumarill, M, shiny|100/100
        |switch|p2a: Great Tusk|Great Tusk|100/100
        |turn|1
        |
        |t:|1697406823
        |-end|p2a: Great Tusk|Protosynthesis|[silent]
        |switch|p2a: Slowking|Slowking-Galar, F|100/100
        |move|p1a: Femboy IX|Belly Drum|p1a: Femboy IX
        |-damage|p1a: Femboy IX|50/100
        |-setboost|p1a: Femboy IX|atk|6|[from] move: Belly Drum
        |-enditem|p1a: Femboy IX|Sitrus Berry|[eat]
        |-heal|p1a: Femboy IX|75/100|[from] item: Sitrus Berry
        |
        """
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_damages = (self.session.query(damages)).all()

        self.assertEqual(query_damages[0].Damage, 50)
        self.assertEqual(query_damages[0].Dealer, "Azumarill")
        self.assertEqual(query_damages[0].Dealer_Player_Number, 1)
        self.assertEqual(query_damages[0].Source_Name, "Belly Drum")
        self.assertEqual(query_damages[0].Receiver, "Azumarill")
        self.assertEqual(query_damages[0].Receiver_Player_Number, 1)
        self.assertEqual(query_damages[0].Turn, 1)
        self.assertEqual(query_damages[0].Type, "Move")

    def test_healing_uploaded(self):
        """
        |turn|1
        ...
        |-damage|p1a: Femboy IX|50/100
        |-setboost|p1a: Femboy IX|atk|6|[from] move: Belly Drum
        |-enditem|p1a: Femboy IX|Sitrus Berry|[eat]
        |-heal|p1a: Femboy IX|75/100|[from] item: Sitrus Berry
        """
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_healing = (self.session.query(healing)).all()

        self.assertEqual(query_healing[0].Healing, 25)
        self.assertEqual(query_healing[0].Receiver, "Azumarill")
        self.assertEqual(query_healing[0].Receiver_Player_Number, 1)
        self.assertEqual(query_healing[0].Source_Name, "Sitrus Berry")
        self.assertEqual(query_healing[0].Turn, 1)
        self.assertEqual(query_healing[0].Type, "Item")

    def test_pivots_uploaded(self):
        """
        |start
        |switch|p1a: Femboy IX|Azumarill, M, shiny|100/100
        |switch|p2a: Great Tusk|Great Tusk|100/100
        """
        self.battle_data_uploader.upload_battle(self.mock_parser)

        query_pivots = (self.session.query(pivots)).all()

        self.assertEqual(query_pivots[0].Pokemon_Enter, "Azumarill")
        self.assertEqual(query_pivots[0].Player_Number, 1)
        self.assertEqual(query_pivots[0].Turn, 0)
        self.assertEqual(query_pivots[0].Source_Name, "action")

    def test_battle_id_already_exists(self):
        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that the battle is in the database
        battle = self.session.query(battle_info).first()
        expected_id = battle.id

        # upload the same battle again
        self.battle_data_uploader.upload_battle(self.mock_parser)

        # check that the battle is still in the database
        battle = (
            self.session.query(battle_info)
            .filter(battle_info.P1 == "massivesket")
            .filter(battle_info.P2 == "Buzzma")
            .first()
        )
        self.assertEqual(battle.id, expected_id)

    def test_upload_error(self):
        # Define the test error data
        battle_url = "test_url"
        error_message = "Test exception"
        traceback = "Test traceback"
        function = "Test function"

        # Call the upload_error method
        self.battle_data_uploader.upload_error(
            battle_url, error_message, traceback, function
        )

        # Verify that the error exists in the database
        with session_scope() as session:
            error_db = session.query(errors).filter_by(Battle_URL=battle_url).first()
            self.assertIsNotNone(error_db)
            self.assertEqual(error_db.Error_Message, error_message)
            self.assertEqual(error_db.Traceback, traceback)
            self.assertEqual(error_db.Function, function)


if __name__ == "__main__":
    unittest.main()
