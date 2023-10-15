import unittest
from unittest.mock import patch, Mock, MagicMock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattlePokemon, MockTurn, MockBattle

# ===bring in object to test===
from . import HealData

"""
NOTE: the mock battle pokemon object assumes all mons start at 100 hp. as a result, we will report the 
values as the negatives relative to 100 because the correct functionality will see the hp as 100 and then the
post-heal hp as something less than 100.
"""


class TestHealData(unittest.TestCase):
    def setUp(self):
        # ==========ALL HEAL TYPE TURNS SETUP HERE ==========
        item_turn = MockTurn(
            1,
            """
            |-heal|p2a: Bisharp|100/100|[from] item: Leftovers
            |upkeep
            """,
        )

        self.item_turn = item_turn

        move_turn = MockTurn(
            22,
            """
            |move|p2a: Moltres|Roost|p2a: Moltres
            |-heal|p2a: Moltres|96/100
            |upkeep
            """,
        )

        self.move_turn = move_turn

        ability_turn = MockTurn(
            22,
            """
            |-heal|p1a: Avalugg|21/100|[from] ability: Ice Body
            |upkeep
            """,
        )

        self.ability_turn = ability_turn

        # note to test this we must assume it had less than 90 hp previously
        regenerator_turn = MockTurn(
            6,
            """
            |switch|p1a: Slowbro|Slowbro, F|90/100
            """,
        )

        self.regenerator_turn = regenerator_turn

        terrain_turn = MockTurn(
            4,
            """
            |-heal|p2a: Tyranitar|91/100|[from] Grassy Terrain
            |upkeep
            """,
        )

        self.terrain_turn = terrain_turn

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

        drain_turn = MockTurn(
            15,
            """
            |move|p1a: Abomasnow|Giga Drain|p2a: Torkoal
            |-damage|p2a: Torkoal|60/100
            |-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal
            |upkeep
            """,
        )

        self.drain_turn = drain_turn

        wish_turn = MockTurn(
            26,
            """
            |turn|26
            |
            |t:|1682240385
            |switch|p2a: Seismitoad|Seismitoad, M|71/100
            |-damage|p2a: Seismitoad|65/100|[from] Stealth Rock
            |move|p1a: Bisharp|Swords Dance|p1a: Bisharp
            |-boost|p1a: Bisharp|atk|2
            |
            |-heal|p2a: Seismitoad|100/100|[from] move: Wish|[wisher] Clefable
            |upkeep
            """,
        )

        self.wish_turn = wish_turn

        # ==========SETUP MODELS FOR TESTING HERE==========
        self.battle_pokemon = MockBattlePokemon()
        self.battle = MockBattle()
        self.battle.turns = [
            self.item_turn,
            self.move_turn,
            self.ability_turn,
            self.regenerator_turn,
            self.terrain_turn,
            self.passive_turn,
            self.drain_turn,
        ]

        self.data_finder = HealData(self.battle, self.battle_pokemon)

    def tearDown(self):
        self.data_finder.heal_data = []

    def test_get_heal_data_move(self):
        event = "|-heal|p2a: Moltres|96/100"
        self.data_finder.get_heal_data(event, self.move_turn)
        heal_data = self.data_finder.heal_data[0]

        self.assertEqual(heal_data["Healing"], -4)
        self.assertEqual(heal_data["Receiver"], "Moltres")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Roost")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Move")

    def test_get_heal_data_delayed_move(self):
        event = "|-heal|p2a: Seismitoad|35/100|[from] move: Wish|[wisher] Clefable"
        self.data_finder.get_heal_data(event, self.wish_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -65)
        self.assertEqual(heal_data["Receiver"], "Seismitoad")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Wish")
        self.assertEqual(heal_data["Turn"], 26)
        self.assertEqual(heal_data["Type"], "Move")

    def test_get_heal_data_item(self):
        event = "|-heal|p2a: Bisharp|35/100|[from] item: Leftovers"
        self.data_finder.get_heal_data(event, self.item_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -65)
        self.assertEqual(heal_data["Receiver"], "Bisharp")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Leftovers")
        self.assertEqual(heal_data["Turn"], 1)
        self.assertEqual(heal_data["Type"], "Item")

    def test_get_heal_data_ability(self):
        event = "|-heal|p1a: Avalugg|21/100|[from] ability: Ice Body"
        self.data_finder.get_heal_data(event, self.ability_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -79)
        self.assertEqual(heal_data["Receiver"], "Avalugg")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Ice Body")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Ability")

    def test_get_heal_data_regenerator(self):
        """
        This is a special case because the heal is not in the turn text. Instead, we will have to analyze every
        pokemon that enters a battle to see if its hp is different from what it was when it left. If it is,
        then we will simply call that an ability heal with the source name Regenerator.
        """
        # to test this, we need to set up the mock_battle_pokemon to believe that Slowbro had less than 90 hp

        event = "|switch|p1a: Slowbro|Slowbro, F|90/100"
        self.data_finder.get_heal_data(event, self.regenerator_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -10)
        self.assertEqual(heal_data["Receiver"], "Slowbro")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Regenerator")
        self.assertEqual(heal_data["Turn"], 6)
        self.assertEqual(heal_data["Type"], "Ability")

    def test_get_heal_data_no_update_if_no_change(self):
        # note that here we set the hp of the swapped in Slowbro to 0 so that it should not trigger a regenerator heal
        # return
        event = "|switch|p1a: Slowbro|Slowbro, F|100/100"
        self.data_finder.get_heal_data(event, self.regenerator_turn)
        self.assertEqual(len(self.data_finder.heal_data), 0)

    def test_get_heal_data_terrain(self):
        event = "|-heal|p2a: Tyranitar|91/100|[from] Grassy Terrain"
        self.data_finder.get_heal_data(event, self.terrain_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -9)
        self.assertEqual(heal_data["Receiver"], "Tyranitar")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_Name"], "Grassy Terrain")
        self.assertEqual(heal_data["Turn"], 4)
        self.assertEqual(heal_data["Type"], "Terrain")

    def test_get_heal_data_passive(self):
        # need to set an initial hp that isn't 0 so that simply returning current
        # hp does not work
        event = "|-heal|p1a: Frosmoth|82/100|[from] Leech Seed"
        self.data_finder.get_heal_data(event, self.passive_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertEqual(heal_data["Healing"], -18)
        self.assertEqual(heal_data["Receiver"], "Frosmoth")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Leech Seed")
        self.assertEqual(heal_data["Turn"], 9)
        self.assertEqual(heal_data["Type"], "Passive")

    def test_get_heal_data_drain(self):
        event = "|-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal"
        self.data_finder.get_heal_data(event, self.drain_turn)
        heal_data = self.data_finder.heal_data[0]
        self.assertAlmostEqual(heal_data["Healing"], -42)
        self.assertEqual(heal_data["Receiver"], "Abomasnow")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_Name"], "Giga Drain")
        self.assertEqual(heal_data["Turn"], 15)
        self.assertEqual(heal_data["Type"], "Drain Move")


if __name__ == "__main__":
    unittest.main()
