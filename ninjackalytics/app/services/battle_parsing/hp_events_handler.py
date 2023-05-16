from typing import Dict, List, Tuple, Protocol

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)


# ============= START PROTOCOLS =============
class Line(Protocol):
    text: str
    number: int


class Turn(Protocol):
    number: int
    text: str
    lines: List[Line]


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...


class HealData(Protocol):
    def get_heal_data(self, event: str, turn: Turn) -> None:
        ...


class DamageData(Protocol):
    def get_damage_data(self, event: str, turn: Turn) -> None:
        ...


# ============= END PROTOCOLS =============


class HpEventsHandler:
    def __init__(self, battle: Battle, heal_data: HealData, damage_data: DamageData):
        self.battle = battle
        self.heal_data = heal_data
        self.damage_data = damage_data

    def handle_events(self):
        """
        Iterates linearly through a battle's lines and checks if an hp event (damage or heal) is present.
        If an hp event is found, calls the corresponding datafinder to analyze the event and store the data.
        This ensures that the hp events are handled linearly such that the battle pokemon object is always
        up to date when called for a respective datafinder.
        """
        for turn in self.battle.get_turns():
            for line in turn.lines:
                if self._is_damage_event(line.text):
                    self.damage_data.get_damage_data(line.text, turn)
                elif self._is_heal_event(line.text):
                    self.heal_data.get_heal_data(line.text, turn)

    def _is_damage_event(self, event: str) -> bool:
        return "|-damage|" in event

    def _is_heal_event(self, event: str) -> bool:
        return "|-heal|" in event or "|switch|" in event

    def get_damage_events(self) -> List[Dict[str, str]]:
        return self.damage_data.damage_events

    def get_heal_events(self) -> List[Dict[str, str]]:
        return self.heal_data.heal_events
