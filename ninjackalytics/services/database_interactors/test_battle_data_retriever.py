import unittest
from unittest.mock import Mock
from datetime import datetime
import os

os.environ["FLASK_ENV"] = "testing"

from ninjackalytics.test_utilities.preppared_battle_objects.base_battle import (
    TestBattle,
)

from ninjackalytics.database.config import TestingConfig
from ninjackalytics.database import Base, engine, SessionLocal
from ninjackalytics.services.database_interactors import (
    BattleDataRetriever,
    BattleDataUploader,
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


class testBattleDataRetriever(unittest.TestCase):
    def setUp(self):
        bd = TestBattle()
        bp = BattlePokemon(bd)
        self.session = SessionLocal()
        Base.metadata.create_all(bind=engine)

        self.battle_parser = BattleParser(bd, bp)
        self.battle_parser.analyze_battle()

        uploader = BattleDataUploader()
        uploader.upload_battle(self.battle_parser)
        self.uploader = uploader
        uploader.close_session()

    def test_get_battle_info(self):
        battle_id = self.uploader.battle_id
        battle_info = BattleDataRetriever().get_battle_info(battle_id)
        self.assertEqual(battle_info["Battle_ID"][0], battle_id)
        self.assertEqual(battle_info["Format"][0], "gen9ou")
        self.assertEqual(battle_info["P1"][0], "massivesket")
        self.assertEqual(battle_info["P2"][0], "Buzzma")
        self.assertEqual(battle_info["Rank"][0], 1337)
        self.assertEqual(battle_info["Winner"][0], "massivesket")


if __name__ == "__main__":
    unittest.main()
