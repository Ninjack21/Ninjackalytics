import unittest
from unittest.mock import Mock

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattle, MockBattlePokemon, MockTurn

# ===bring in object to test===
from .damages import DamageData


class TestDamageData(unittest.TestCase):
    def setUp(self):
        mock_battle = MockBattle()
        mock_battle_pokemon = MockBattlePokemon()
        self.damage_data = DamageData(mock_battle, mock_battle_pokemon)

    def tearDown(self):
        self.damage_data.damage_events = []

    def test_get_dmg_data(self):
        move_turn = MockTurn(
            1,
            """
                |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
                |-damage|p1a: Cuss-Tran|67/100
                """,
        )

        event = "|-damage|p1a: Cuss-Tran|67/100"

        self.damage_data.get_damage_data(event, move_turn)
        dmg_data = self.damage_data.damage_events[0]

        self.assertEqual(dmg_data["Damage"], 33)
        self.assertEqual(dmg_data["Dealer"], "Blissey")
        self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
        self.assertEqual(dmg_data["Source_Name"], "Seismic Toss")
        self.assertEqual(dmg_data["Receiver"], "Cuss-Tran")
        self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
        self.assertEqual(dmg_data["Turn"], 1)
        self.assertEqual(dmg_data["Type"], "Move")

    def test_get_item_data(self):
        event = "|-damage|p2a: BrainCell|50/100|[from] item: Life Orb"
        turn = MockTurn(1, event)

        self.damage_data.get_damage_data(event, turn)
        item_data = self.damage_data.damage_events[0]

        self.assertEqual(item_data["Damage"], 50)
        self.assertEqual(item_data["Dealer"], "Life Orb")
        self.assertEqual(item_data["Dealer_Player_Number"], 2)
        self.assertEqual(item_data["Source_Name"], "Life Orb")
        self.assertEqual(item_data["Receiver"], "BrainCell")
        self.assertEqual(item_data["Receiver_Player_Number"], 2)
        self.assertEqual(item_data["Turn"], 1)
        self.assertEqual(item_data["Type"], "Item")

    def test_get_ability_data(self):
        event = "|-damage|p1a: Pikachu|80/100|[from] ability: Static"
        turn = MockTurn(1, event)

        self.damage_data.get_damage_data(event, turn)
        ability_data = self.damage_data.damage_events[0]

        self.assertEqual(ability_data["Damage"], 20)
        self.assertEqual(ability_data["Dealer"], "Static")
        self.assertEqual(ability_data["Dealer_Player_Number"], 1)
        self.assertEqual(ability_data["Source_Name"], "Static")
        self.assertEqual(ability_data["Receiver"], "Pikachu")
        self.assertEqual(ability_data["Receiver_Player_Number"], 1)
        self.assertEqual(ability_data["Turn"], 1)
        self.assertEqual(ability_data["Type"], "Ability")

    def test_get_hazard_data(self):
        event = "|-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock"
        turn = MockTurn(1, event)

        self.damage_data.get_damage_data(event, turn)
        dmg_data = self.damage_data.damage_events[0]

        self.assertEqual(dmg_data["Damage"], 6)
        self.assertEqual(dmg_data["Dealer"], "Stealth Rock")
        self.assertEqual(dmg_data["Dealer_Player_Number"], 1)
        self.assertEqual(dmg_data["Source_Name"], "Stealth Rock")
        self.assertEqual(dmg_data["Receiver"], "Ferrothorn")
        self.assertEqual(dmg_data["Receiver_Player_Number"], 2)
        self.assertEqual(dmg_data["Turn"], 1)
        self.assertEqual(dmg_data["Type"], "Hazard")

    def test_get_status_data(self):
        event = "|-damage|p1a: Rillaboom|94/100 tox|[from] psn"
        turn = MockTurn(1, event)

        self.damage_data.get_damage_data(event, turn)
        dmg_data = self.damage_data.damage_events[0]

        self.assertEqual(dmg_data["Damage"], 6)
        self.assertEqual(dmg_data["Dealer"], "tox")
        self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
        self.assertEqual(dmg_data["Source_Name"], "tox")
        self.assertEqual(dmg_data["Receiver"], "Rillaboom")
        self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
        self.assertEqual(dmg_data["Turn"], 1)
        self.assertEqual(dmg_data["Type"], "Status")

    def test_get_passive_data(self):
        event = "|-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn"
        turn = MockTurn(1, event)

        self.damage_data.get_damage_data(event, turn)
        dmg_data = self.damage_data.damage_events[0]

        self.assertEqual(dmg_data["Damage"], 12)
        self.assertEqual(dmg_data["Dealer"], "Ferrothorn")
        self.assertEqual(dmg_data["Dealer_Player_Number"], 2)
        self.assertEqual(dmg_data["Source_Name"], "Leech Seed")
        self.assertEqual(dmg_data["Receiver"], "Druddigon")
        self.assertEqual(dmg_data["Receiver_Player_Number"], 1)
        self.assertEqual(dmg_data["Turn"], 1)
        self.assertEqual(dmg_data["Type"], "Passive")


if __name__ == "__main__":
    unittest.main()
