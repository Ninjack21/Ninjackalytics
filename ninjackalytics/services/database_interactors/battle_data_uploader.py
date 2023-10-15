from typing import Dict, List

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


class BattleDataUploader:
    def __init__(self):
        self.session = SessionLocal()
        self.p1_team_id = None
        self.p2_team_id = None
        self.battle_id = None

    def close_session(self):
        self.session.close()

    def _upload_teams(self, teams_list: List[Dict[str, str]]) -> int:
        for pnum, team in enumerate(teams_list):
            mon_names = [mon_name for mon_name in team.values()]
            mon_names.sort()
            # re-assign mons after sorting
            for i, mon in enumerate(mon_names):
                team[f"Pok{i+1}"] = mon

            team_db = teams(**team)
            self.session.add(team_db)
            self.session.commit()
            self.session.refresh(team_db)
            if pnum == 0:
                self.p1_team_id = team_db.id
            else:
                self.p2_team_id = team_db.id

    def _upload_general_info(self, general_info: Dict[str, str]) -> int:
        """
        Uploads battle info to the database and returns the battle's id
        """
        general_info["P1_team"] = self.p1_team_id
        general_info["P2_team"] = self.p2_team_id
        battle_info_db = battle_info(**general_info)
        self.session.add(battle_info_db)
        self.session.commit()
        self.session.refresh(battle_info_db)
        self.battle_id = battle_info_db.id

    def _upload_actions(self, actions_list: List[Dict[str, str]]) -> None:
        for action in actions_list:
            action["Battle_ID"] = self.battle_id
            action_db = actions(**action)
            self.session.add(action_db)
        self.session.commit()

    def _upload_damages(self, damages_list: List[Dict[str, str]]) -> None:
        for damage in damages_list:
            damage["Battle_ID"] = self.battle_id
            damage_db = damages(**damage)
            self.session.add(damage_db)
        self.session.commit()

    def _upload_healing(self, healing_list: List[Dict[str, str]]) -> None:
        for heal in healing_list:
            heal["Battle_ID"] = self.battle_id
            heal_db = healing(**heal)
            self.session.add(heal_db)
        self.session.commit()

    def _upload_pivots(self, pivots_list: List[Dict[str, str]]) -> None:
        for pivot in pivots_list:
            pivot["Battle_ID"] = self.battle_id
            pivot_db = pivots(**pivot)
            self.session.add(pivot_db)
        self.session.commit()

    def upload_battle(self, parser: BattleParser) -> None:
        """
        Uploads the data from the BattleParser to the database
        """
        self._upload_teams(parser.teams)
        self._upload_general_info(parser.general_info)
        self._upload_actions(parser.actions)
        self._upload_damages(parser.damages)
        self._upload_healing(parser.healing)
        self._upload_pivots(parser.pivots)
