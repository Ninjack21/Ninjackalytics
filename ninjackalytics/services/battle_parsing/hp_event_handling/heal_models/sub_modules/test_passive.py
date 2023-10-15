import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn

# ===bring in object to test===
from . import PassiveHealData


class TestPassiveHealData(unittest.TestCase):
    def setUp(self):
        # leech seed example - can find source by damage immediately preceeding
        # I am not sure that you can do that for all [silent] heals
        passive_turn = MockTurn(
            9,
            """
            |-damage|p2a: Skarmory|25/100|[from] Leech Seed|[of] p1a: Frosmoth
            |-heal|p1a: Frosmoth|82/100 tox|[silent]
            |upkeep
            """,
        )

        self.passive_turn = passive_turn
        mock_battle_pokemon = MockBattlePokemon()
        self.data_finder = PassiveHealData(mock_battle_pokemon)

    def test_get_heal_data_passive(self):
        # need to set an initial hp that isn't 0 so that simply returning current
        # hp does not work
        self.data_finder.battle_pokemon.update_hp_for_pokemon("p1a: Frosmoth", 50)
        event = "|-heal|p1a: Frosmoth|82/100|[from] Leech Seed"
        heal_data = self.data_finder.get_heal_data(event, self.passive_turn)
        self.assertEqual(heal_data["Healing"], 32)
        self.assertEqual(heal_data["Receiver"], "Frosmoth")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Leech Seed")
        self.assertEqual(heal_data["Turn"], 9)
        self.assertEqual(heal_data["Type"], "Passive")


if __name__ == "__main__":
    unittest.main()
