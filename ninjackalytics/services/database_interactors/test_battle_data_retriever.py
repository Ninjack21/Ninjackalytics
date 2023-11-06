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

        self.retriever = BattleDataRetriever()

    def test_get_battle_info(self):
        battle_id = self.uploader.battle_id
        battle_info = self.retriever.get_battle_info(battle_id)
        self.assertEqual(battle_info["Battle_ID"][0], battle_id)
        self.assertEqual(battle_info["Format"][0], "gen9ou")
        self.assertEqual(battle_info["P1"][0], "massivesket")
        self.assertEqual(battle_info["P2"][0], "Buzzma")
        self.assertEqual(battle_info["Rank"][0], 1337)
        self.assertEqual(battle_info["Winner"][0], "massivesket")

    def test_get_teams(self):
        battle_id = self.uploader.battle_id
        teams = self.retriever.get_teams(battle_id)
        self.assertEqual(teams["Pok1"][0], "Azumarill")
        self.assertEqual(teams["Pok2"][0], "Garganacl")
        self.assertEqual(teams["Pok3"][0], "Great Tusk")
        self.assertEqual(teams["Pok4"][0], "Iron Valiant")
        self.assertEqual(teams["Pok5"][0], "Ogerpon-Wellspring")
        self.assertEqual(teams["Pok6"][0], "Sneasler")
        self.assertEqual(teams["Pok1"][1], "Corviknight")
        self.assertEqual(teams["Pok2"][1], "Gliscor")
        self.assertEqual(teams["Pok3"][1], "Great Tusk")
        self.assertEqual(teams["Pok4"][1], "Iron Valiant")
        self.assertEqual(teams["Pok5"][1], "Kingambit")
        self.assertEqual(teams["Pok6"][1], "Slowking-Galar")

    def test_get_actions(self):
        battle_id = self.uploader.battle_id
        allactions = self.retriever.get_actions(battle_id)
        # found actions in turn 1 for p1 and p2 but not going to be overly rigorous
        self.assertEqual(
            allactions["Action"]
            .loc[(allactions["Player_Number"] == 1) & (allactions["Turn"] == 1)]
            .iloc[0],
            "move",
        )
        self.assertEqual(
            allactions["Action"]
            .loc[(allactions["Player_Number"] == 2) & (allactions["Turn"] == 1)]
            .iloc[0],
            "switch",
        )

    def test_get_damages(self):
        battle_id = self.uploader.battle_id
        alldamages = self.retriever.get_damages(battle_id)
        # found damages in turn 1 and 2 for p1 and p2 but not going to be overly rigorous
        self.assertEqual(
            alldamages["Damage"]
            .loc[
                (alldamages["Receiver_Player_Number"] == 1) & (alldamages["Turn"] == 1)
            ]
            .iloc[0],
            50,
        )
        self.assertEqual(
            alldamages["Damage"]
            .loc[
                (alldamages["Receiver_Player_Number"] == 2) & (alldamages["Turn"] == 2)
            ]
            .iloc[0],
            100,
        )

    def test_get_healing(self):
        battle_id = self.uploader.battle_id
        allhealing = self.retriever.get_healing(battle_id)
        # found healing in turn 1 for p1 (only healing in battle)
        self.assertEqual(
            allhealing["Healing"]
            .loc[
                (allhealing["Receiver_Player_Number"] == 1) & (allhealing["Turn"] == 1)
            ]
            .iloc[0],
            25,
        )

    def test_get_pivots(self):
        battle_id = self.uploader.battle_id
        allpivots = self.retriever.get_pivots(battle_id)
        # found pivots in turn 1 for p2 (only pivot in battle)
        pivot = allpivots.loc[
            (allpivots["Player_Number"] == 2) & (allpivots["Turn"] == 1)
        ].iloc[0]
        self.assertEqual(pivot["Pokemon_Enter"], "Slowking-Galar")
        self.assertEqual(pivot["Player_Number"], 2)
        self.assertEqual(pivot["Source_Name"], "action")
        self.assertEqual(pivot["Turn"], 1)


if __name__ == "__main__":
    unittest.main()
