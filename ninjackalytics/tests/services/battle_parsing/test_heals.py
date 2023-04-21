import unittest
from unittest.mock import patch, Mock, MagicMock

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.heals import HealData, Turn, Battle, BattlePokemon


# =================== MOCK PROTOCOLS FOR TESTING ===================
# based on protocol in models
class MockBattlePokemon:
    def __init__(self):
        self.mon_hps = {}
        self.mon_hp_changes = {}

    # quick implementation for testing
    def get_pnum_and_name(self, raw_name):
        """
        example raw_name = 'p1a: May Day Parade'
        """
        pnum_split_name = raw_name.split(": ")
        pnum = int(pnum_split_name[0][1])
        name = pnum_split_name[1]
        return pnum, name

        self.mock_battle_pokemon = MockBattlePokemon()

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        # assumes not called before get_current_hp, which inits mon_hps
        current_hp = self.mon_hps[raw_name]
        self.mon_hp_changes[raw_name] = current_hp - new_hp
        self.mon_hps[raw_name] = new_hp

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        if not raw_name in self.mon_hps:
            # set to 0 so that healing can be calculated
            self.mon_hps[raw_name] = 0.0
        return self.mon_hps[raw_name]


mock_battle_pokemon = MockBattlePokemon()


class MockBattle:
    def __init__(self):
        turns = []

    # quick implementation for testing
    def get_turns(self) -> list:
        return self.turns


mock_battle = MockBattle()


class MockTurn:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


# =================== MOCK PROTOCOLS FOR TESTING ===================


class TestHealData(unittest.TestCase):
    def setUp(self):
        # ==========ALL HEAL TYPE TURNS SETUP HERE ==========
        item_turn = Mock(Turn)
        item_turn.number = 1
        item_turn.text = """
            |-heal|p2a: Bisharp|100/100|[from] item: Leftovers
            |upkeep
            """

        self.item_turn = item_turn

        move_turn = Mock(Turn)
        move_turn.number = 22
        move_turn.text = """
            |move|p2a: Moltres|Roost|p2a: Moltres
            |-heal|p2a: Moltres|96/100
            |upkeep
            """

        self.move_turn = move_turn

        ability_turn = Mock(Turn)
        ability_turn.number = 22
        ability_turn.text = """
            |-heal|p1a: Avalugg|21/100|[from] ability: Ice Body
            |upkeep
            """

        self.ability_turn = ability_turn

        # note to test this we must assume it had less than 90 hp previously
        regenerator_turn = Mock(Turn)
        regenerator_turn.number = 6
        regenerator_turn.text = """
            |switch|p1a: Slowbro|Slowbro, F|90/100
            """

        self.regenerator_turn = regenerator_turn

        terrain_turn = Mock(Turn)
        terrain_turn.number = 4
        terrain_turn.text = """
            |-heal|p2a: Tyranitar|91/100|[from] Grassy Terrain
            |upkeep
            """

        self.terrain_turn = terrain_turn

        # leech seed example - can find source by damage immediately preceeding
        # I am not sure that you can do that for all [silent] heals
        passive_turn = Mock(Turn)
        passive_turn.number = 9
        passive_turn.text = """
            |-damage|p2a: Skarmory|25/100|[from] Leech Seed|[of] p1a: Frosmoth
            |-heal|p1a: Frosmoth|82/100 tox|[silent]
            |upkeep
            """

        self.passive_turn = passive_turn

        drain_turn = Mock(Turn)
        drain_turn.number = 15
        drain_turn.text = """
            |move|p1a: Abomasnow|Giga Drain|p2a: Torkoal
            |-damage|p2a: Torkoal|60/100
            |-heal|p1a: Abomasnow|58/100|[from] drain|[of] p2a: Torkoal
            |upkeep
            """

        self.drain_turn = drain_turn

        # ==========SETUP MODELS FOR TESTING HERE==========
        self.battle_pokemon = mock_battle_pokemon
        self.battle = mock_battle
        self.battle.turns = [
            self.item_turn,
            self.move_turn,
            self.ability_turn,
            self.regenerator_turn,
            self.terrain_turn,
            self.passive_turn,
            self.drain_turn,
        ]

        self.heal_data = HealData(self.battle, self.battle_pokemon)

    def test_get_heal_data_move(self):
        heal_data = self.heal_data.get_heal_data(self.move_turn)
        self.assertEqual(heal_data["Healing"], 96)
        self.assertEqual(heal_data["Receiver"], "Moltres")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_name"], "Roost")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Move")

    def test_get_heal_data_item(self):
        heal_data = self.heal_data.get_heal_data(self.item_turn)
        self.assertEqual(heal_data["Healing"], 100)
        self.assertEqual(heal_data["Receiver"], "Bisharp")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_name"], "Leftovers")
        self.assertEqual(heal_data["Turn"], 1)
        self.assertEqual(heal_data["Type"], "Item")

    def test_get_heal_data_ability(self):
        heal_data = self.heal_data.get_heal_data(self.ability_turn)
        self.assertEqual(heal_data["Healing"], 21)
        self.assertEqual(heal_data["Receiver"], "Avalugg")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_name"], "Ice Body")
        self.assertEqual(heal_data["Turn"], 22)
        self.assertEqual(heal_data["Type"], "Ability")

    def test_get_heal_data_regenerator(self):
        """
        This is a special case because the heal is not in the turn text. Instead, we will have to analyze every
        pokemon that enters a battle to see if its hp is different from what it was when it left. If it is,
        then we will simply call that an ability heal with the source name Regenerator.
        """
        heal_data = self.heal_data.get_heal_data(self.regenerator_turn)
        self.assertEqual(heal_data["Healing"], 90)
        self.assertEqual(heal_data["Receiver"], "Slowbro")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_name"], "Regenerator")
        self.assertEqual(heal_data["Turn"], 6)
        self.assertEqual(heal_data["Type"], "Ability")

    def test_get_heal_data_terrain(self):
        heal_data = self.heal_data.get_heal_data(self.terrain_turn)
        self.assertEqual(heal_data["Healing"], 91)
        self.assertEqual(heal_data["Receiver"], "Tyranitar")
        self.assertEqual(heal_data["Receiver_Player_Number"], 2)
        self.assertEqual(heal_data["Source_name"], "Grassy Terrain")
        self.assertEqual(heal_data["Turn"], 4)
        self.assertEqual(heal_data["Type"], "Terrain")

    def test_get_heal_data_passive(self):
        heal_data = self.heal_data.get_heal_data(self.passive_turn)
        self.assertEqual(heal_data["Healing"], 82)
        self.assertEqual(heal_data["Receiver"], "Frosmoth")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_name"], "Leech Seed")
        self.assertEqual(heal_data["Turn"], 9)
        self.assertEqual(heal_data["Type"], "Passive")

    def test_get_heal_data_drain(self):
        heal_data = self.heal_data.get_heal_data(self.drain_turn)
        self.assertEqual(heal_data["Healing"], 58)
        self.assertEqual(heal_data["Receiver"], "Abomasnow")
        self.assertEqual(heal_data["Receiver_Player_Number"], 1)
        self.assertEqual(heal_data["Source_name"], "Torkoal")
        self.assertEqual(heal_data["Turn"], 15)
        self.assertEqual(heal_data["Type"], "Drain")


if __name__ == "__main__":
    unittest.main()
