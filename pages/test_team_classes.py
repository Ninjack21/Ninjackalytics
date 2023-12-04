import unittest
from unittest.mock import Mock
from team_classes import WinrateCalculator


class TestWinrateCalculator(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock()
        self.mock_format_data = Mock()
        self.antimeta_calculator = WinrateCalculator(self.mock_format_data, "antimeta")

        # winrate calc only looks at top30 and pvpmetadata from format_data object
        self.mock_format_data.top30 = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Popularity": [60, 60, 60, 12],
                "Format": ["[Gen 9] OU", "[Gen 9] OU", "[Gen 9] OU", "[Gen 9] OU"],
                "Winrate": [60, 55, 45, 40],
                "SampleSize": [100, 100, 100, 20],  # Squirtle has too few samples
            }
        )
        self.mock_format_data.format_pvpmetadata = pd.DataFrame(
            {
                "Format": [
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                ],
                "Pokemon1": [
                    "Pikachu",
                    "Pikachu",
                    "Pikachu",
                    "Pikachu",
                    "Charizard",
                    "Charizard",
                    "Charizard",
                    "Bulbarsaur",
                    "Bulbarsaur",
                    "Squirtle",
                ],
                "Pokemon2": [
                    "Charizard",
                    "Bulbasaur",
                    "Squirtle",
                    "Pikachu",
                    "Bulbasaur",
                    "Squirtle",
                    "Charizard",
                    "Squirtle",
                    "Bulbasaur",
                    "Squirtle",
                ],
                "Winrate": [
                    60,  # Pikachu vs Charizard
                    70,  # Pikachu vs Bulbasaur
                    80,  # Pikachu vs Squirtle
                    50,  # Pikachu vs Pikachu
                    90,  # Charizard vs Bulbasaur
                    55,  # Charizard vs Squirtle
                    50,  # Charizard vs Charizard
                    60,  # Bulbasaur vs Squirtle
                    50,  # Bulbasaur vs Bulbasaur
                    50,  # Squirtle vs Squirtle
                ],
                "SampleSize": [
                    50,  # Pikachu vs Charizard
                    30,  # Pikachu vs Bulbasaur
                    10,  # Pikachu vs Squirtle
                    100,  # Pikachu vs Pikachu
                    15,  # Charizard vs Bulbasaur
                    5,  # Charizard vs Squirtle
                    20,  # Charizard vs Charizard
                    5,  # Bulbasaur vs Squirtle
                    10,  # Bulbasaur vs Bulbasaur
                    100,  # Squirtle vs Squirtle
                ],
            }
        )
        # NOTE: the SampleSizes and Winrates are not technically possible but are used for testing purposes

    def test_get_mon_vs_mon_winrates(self):
        self.mock_format_data.format_pvpmetadata = pd.DataFrame(
            {
                "Pokemon1": ["Pikachu", "Charizard", "Bulbasaur", "Pikachu"],
                "Pokemon2": ["Charizard", "Bulbasaur", "Pikachu", "Squirtle"],
                "Winrate": [60, 70, 80, 90],
            }
        )
        team = ["Pikachu", "Charizard"]
        top30mon = "Charizard"
        (
            team_mons_in_pok1,
            team_mons_in_pok2,
        ) = self.antimeta_calculator._get_mon_vs_mon_winrates(top30mon, team)
        self.assertEqual(
            team_mons_in_pok1.shape, (1, 3)
        )  # Check that the result is a DataFrame with the expected shape
        self.assertEqual(
            team_mons_in_pok2.shape, (1, 3)
        )  # Check that the result is a DataFrame with the expected shape
        self.assertEqual(
            team_mons_in_pok1["Pokemon1"].values[0], "Pikachu"
        )  # Check that the correct rows were selected
        self.assertEqual(
            team_mons_in_pok2["Pokemon2"].values[0], "Pikachu"
        )  # Check that the correct rows were selected


if __name__ == "__main__":
    unittest.main()
