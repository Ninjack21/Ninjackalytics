import unittest

# ===bring in base test utilities objects===
from ninjackalytics.test_utilities.utils import MockBattle, MockBattlePokemon, MockTurn


# ===bring in object to test===
from .receiver_finder import ReceiverFinder


class TestReceiverFinder(unittest.TestCase):
    def setUp(self):
        mock_battle_pokemon = MockBattlePokemon()
        self.receiver_finder = ReceiverFinder(mock_battle_pokemon)

    def test_get_receiver(self):
        # Define some test cases
        test_cases = [
            ("|-damage|p1a: Blissey|67/100", (1, "Blissey")),
            ("|-damage|p2a: Incineroar|67/100", (2, "Incineroar")),
            ("|-damage|p1a: Cuss-Tran|67/100", (1, "Cuss-Tran")),
        ]

        for event, expected_output in test_cases:
            self.assertEqual(
                self.receiver_finder.get_receiver(event),
                expected_output,
            )


if __name__ == "__main__":
    unittest.main()
