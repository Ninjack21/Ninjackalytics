import unittest
from unittest.mock import Mock


# ===bring in object to test===
from . import HpEventsHandler


class TestHpEventsHandler(unittest.TestCase):
    def setUp(self):
        self.heal_data = Mock()
        self.damage_data = Mock()
        self.battle = Mock()
        self.hp_events_handler = HpEventsHandler(
            self.battle, self.heal_data, self.damage_data
        )

    def test_handle_damage_events(self):
        damage_event = "|-damage|..."
        turn = Mock()
        line = Mock()
        line.text = damage_event
        turn.lines = [line]
        self.battle.get_turns.return_value = [turn]

        self.hp_events_handler.handle_events()

        self.damage_data.get_damage_data.assert_called_once_with(damage_event, turn)
        self.heal_data.get_heal_data.assert_not_called()

    def test_handle_heal_events(self):
        heal_event = "|-heal|..."
        turn = Mock()
        line = Mock()
        line.text = heal_event
        turn.lines = [line]
        self.battle.get_turns.return_value = [turn]

        self.hp_events_handler.handle_events()

        self.heal_data.get_heal_data.assert_called_once_with(heal_event, turn)
        self.damage_data.get_damage_data.assert_not_called()


if __name__ == "__main__":
    unittest.main()
