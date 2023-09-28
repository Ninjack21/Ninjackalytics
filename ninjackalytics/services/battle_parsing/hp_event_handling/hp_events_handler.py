from typing import Dict, List, Tuple, Protocol
from ninjackalytics.protocols.battle_initialization.protocols import Line, Turn, Battle


# ============= START PROTOCOLS =============


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
        return self.heal_data.heal_data
