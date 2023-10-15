import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import AbilityHealData


class TestAbilityHealData(unittest.TestCase):
    def setUp(self):
        ability_turn = MockTurn(
            22,
            """
            |-heal|p1a: Avalugg|21/100|[from] ability: Ice Body
            |upkeep
            """,
        )

        self.ability_turn = ability_turn
        mock_battle_pokemon = MockBattlePokemon()

        self.data_finder = AbilityHealData(mock_battle_pokemon)

    def test_get_heal_data_ability(self):
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p1a: Avalugg", 10)
        event = "|-heal|p1a: Avalugg|21/100|[from] ability: Ice Body"
        heal_data = self.data_finder.get_heal_data(event, self.ability_turn)
        self.assertEqual(heal_data["Healing"], 11)
        self.assertEqual(heal_data["Receiver"], "Avalugg")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Ice Body")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Ability")


if __name__ == "__main__":
    unittest.main()
