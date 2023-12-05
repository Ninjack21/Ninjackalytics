import unittest
from unittest.mock import Mock
import pandas as pd
from .team_classes import WinrateCalculator


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
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                    "[Gen 9] OU",
                ],
                "Pokemon1": [
                    "Pikachu",  # 1
                    "Pikachu",  # 2
                    "Pikachu",  # 3
                    "Pikachu",  # 4
                    "Charizard",  # 5
                    "Charizard",  # 6
                    "Charizard",  # 7
                    "Bulbarsaur",  # 8
                    "Bulbarsaur",  # 9
                    "Squirtle",  # 10
                ],
                "Pokemon2": [
                    "Charizard",  # 1
                    "Bulbasaur",  # 2
                    "Squirtle",  # 3
                    "Pikachu",  # 4
                    "Bulbasaur",  # 5
                    "Squirtle",  # 6
                    "Charizard",  # 7
                    "Squirtle",  # 8
                    "Bulbasaur",  # 9
                    "Squirtle",  # 10
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
        top30mon = "Pikachu"
        team = ["Charizard", "Bulbasaur", "Squirtle"]

        # none of the team mons are in pokemon1 where pikachu is in pokemon2
        expected_team_mon_in_pokemon1 = pd.DataFrame(
            {
                "Format": [],
                "Pokemon1": [],
                "Pokemon2": [],
                "Winrate": [],
                "SampleSize": [],
            }
        )

        expected_team_mon_in_pokemon2 = pd.DataFrame(
            {
                "Format": ["[Gen 9] OU", "[Gen 9] OU", "[Gen 9] OU"],
                "Pokemon1": ["Pikachu", "Pikachu", "Pikachu"],
                "Pokemon2": ["Charizard", "Bulbasaur", "Squirtle"],
                "Winrate": [60, 70, 80],
                "SampleSize": [50, 30, 10],
            },
        )

        (
            actual_team_mon_in_pok1,
            actual_team_mon_in_pok2,
        ) = self.antimeta_calculator._get_mon_vs_mon_winrates(top30mon, team)

        self.assertEqual(len(actual_team_mon_in_pok1), 0)
        pd.testing.assert_frame_equal(
            expected_team_mon_in_pokemon2.reset_index(),
            actual_team_mon_in_pok2.reset_index(),
            check_like=True,
        )


if __name__ == "__main__":
    unittest.main()
