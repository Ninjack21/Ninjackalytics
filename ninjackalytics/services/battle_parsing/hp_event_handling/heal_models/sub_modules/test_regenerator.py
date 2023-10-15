import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import RegeneratorHealData


class TestRegeneratorHealData(unittest.TestCase):
    def setUp(self):
        # note to test this we must assume it had less than 90 hp previously
        regenerator_turn = MockTurn(
            6,
            """
            |switch|p1a: Slowbro|Slowbro, F|90/100
            """,
        )

        self.regenerator_turn = regenerator_turn
        mock_battle_pokemon = MockBattlePokemon()

        self.data_finder = RegeneratorHealData(mock_battle_pokemon)

    def test_get_heal_data_regenerator(self):
        """
        This is a special case because the heal is not in the turn text. Instead, we will have to analyze every
        pokemon that enters a battle to see if its hp is different from what it was when it left. If it is,
        then we will simply call that an ability heal with the source name Regenerator.
        """
        # to test this, we need to set up the mock_battle_pokemon to believe that Slowbro had less than 90 hp
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p1a: Slowbro", 40)

        event = "|switch|p1a: Slowbro|Slowbro, F|90/100"
        heal_data = self.data_finder.get_heal_data(event, self.regenerator_turn)
        self.assertEqual(heal_data["Healing"], 50)
        self.assertEqual(heal_data["Receiver"], "Slowbro")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Regenerator")
        self.assertEqual(heal_data["Turn"], 6)
        self.assertEqual(heal_data["Type"], "Ability")

    def test_get_heal_data_no_update_if_no_change(self):
        """
        This is a special case because the heal is not in the turn text. Instead, we will have to analyze every
        pokemon that enters a battle to see if its hp is different from what it was when it left. If it is,
        then we will simply call that an ability heal with the source name Regenerator.
        """
        # to test this, we need to set up the mock_battle_pokemon to believe that Slowbro had less than 90 hp
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p1a: Slowbro", 90)

        event = "|switch|p1a: Slowbro|Slowbro, F|90/100"
        heal_data = self.data_finder.get_heal_data(event, self.regenerator_turn)
        self.assertIsNone(heal_data)


if __name__ == "__main__":
    unittest.main()
