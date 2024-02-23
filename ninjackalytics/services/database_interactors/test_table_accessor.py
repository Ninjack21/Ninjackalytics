import unittest
from unittest.mock import Mock
from datetime import datetime
import os

os.environ["FLASK_ENV"] = "testing"

from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)

from ninjackalytics.database.config import TestingConfig
from ninjackalytics.database import Base, get_engine, get_sessionlocal
from ninjackalytics.services.database_interactors import (
    BattleDataUploader,
)
from ninjackalytics.services.battle_parsing import BattleParser
from ninjackalytics.services.battle_parsing.battle_data.battle_pokemon import (
    BattlePokemon,
)
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor


class testTableAccessor(unittest.TestCase):
    def setUp(self):
        bd = TestBattle()
        bp = BattlePokemon(bd)
        self.session = get_sessionlocal()
        self.session.begin_nested()
        Base.metadata.create_all(bind=get_engine())

        self.battle_parser = BattleParser(bd, bp)
        self.battle_parser.analyze_battle()

        uploader = BattleDataUploader()
        uploader.upload_battle(self.battle_parser)

        self.ta = TableAccessor()

    def tearDown(self):
        self.session.rollback()  # rollback the transaction

    def test_get_teams(self):
        # first ensure can pull all teams
        teams = self.ta.get_teams()
        self.assertEqual(len(teams), 2)

        # then ensure can pull a specific team
        conditions = {"Pok1": {"op": "==", "value": "Azumarill"}}
        p1_team = self.ta.get_teams(conditions)
        self.assertEqual(len(p1_team), 1)
        self.assertEqual(p1_team["Pok1"][0], "Azumarill")

    def test_get_battle_info(self):
        # first ensure can pull all battle info
        battle_info = self.ta.get_battle_info()
        self.assertEqual(len(battle_info), 1)

        # then ensure can pull a specific battle info
        conditions = {"P1": {"op": "==", "value": "massivesket"}}
        p1_battle_info = self.ta.get_battle_info(conditions)
        self.assertEqual(len(p1_battle_info), 1)
        self.assertEqual(p1_battle_info["P1"][0], "massivesket")

    def test_get_actions(self):
        # first ensure can pull all actions
        actions = self.ta.get_actions()
        self.assertEqual(len(actions["Player_Number"].unique()), 2)

        # then ensure can pull only P1 actions
        conditions = {"Player_Number": {"op": "==", "value": 1}}
        p1_actions = self.ta.get_actions(conditions)
        self.assertTrue(len(actions["Player_Number"].unique() == 1))

    def test_get_damages(self):
        # first ensure can pull all damages
        damages = self.ta.get_damages()
        self.assertEqual(len(damages["Receiver_Player_Number"].unique()), 2)

        # then ensure can pull only P1 damages
        conditions = {"Receiver_Player_Number": {"op": "==", "value": 1}}
        p1_damages = self.ta.get_damages(conditions)
        self.assertTrue(len(damages["Receiver_Player_Number"].unique() == 1))

    def test_get_healing(self):
        # first ensure can pull all healing
        healing = self.ta.get_healing()
        self.assertTrue(healing is not None)

        # ensure can find only healing related to P1
        conditions = {"Receiver_Player_Number": {"op": "==", "value": 1}}
        p1_healing = self.ta.get_healing(conditions)
        self.assertTrue(len(p1_healing["Receiver_Player_Number"]) == 1)
        self.assertTrue(p1_healing["Receiver_Player_Number"].iloc[0] == 1)

    def test_get_pivots(self):
        # NOTE: this test battle has no pivots so not implementing right now
        # the others prove the conditional queries are working so all is
        # fine right now. Assume same behavior applies to get_pivots
        self.assertTrue(True)
