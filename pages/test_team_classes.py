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
                "SampleSize": [100, 100, 100, 100],
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
                    "Bulbasaur",  # 8
                    "Bulbasaur",  # 9
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
                    5,  # Pikachu vs Squirtle
                    100,  # Pikachu vs Pikachu
                    20,  # Charizard vs Bulbasaur
                    5,  # Charizard vs Squirtle
                    20,  # Charizard vs Charizard
                    5,  # Bulbasaur vs Squirtle
                    20,  # Bulbasaur vs Bulbasaur
                    5,  # Squirtle vs Squirtle
                ],
            }
        )

        self.wr_calc = WinrateCalculator(self.mock_format_data, "antimeta")

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

    def test_get_mon_vs_mon_winrates_drops_duplicates(self):
        """
        discovered that if a top30 mon is on your team and in the top30 then it will check itself against itself.
        this is by default 50 BUT it will find that in both the mon1 and mon2 columns, doubling the entry
        """
        top30mon = "Pikachu"
        team = ["Pikachu"]

        expected_team_mon_in_pokemon1 = pd.DataFrame(
            {
                "Format": ["[Gen 9] OU"],
                "Pokemon1": ["Pikachu"],
                "Pokemon2": ["Pikachu"],
                "Winrate": [50],
                "SampleSize": [100],
            }
        )

        expected_team_mon_in_pokemon2 = pd.DataFrame(
            {
                "Format": [],
                "Pokemon1": [],
                "Pokemon2": [],
                "Winrate": [],
                "SampleSize": [],
            }
        )

        (
            actual_team_mon_in_pok1,
            actual_team_mon_in_pok2,
        ) = self.antimeta_calculator._get_mon_vs_mon_winrates(top30mon, team)

        pd.testing.assert_frame_equal(
            expected_team_mon_in_pokemon1.reset_index(drop=True),
            actual_team_mon_in_pok1.reset_index(drop=True),
            check_like=True,
        )
        # this should be empty because we choose to ignore the entry in pok2
        self.assertEqual(len(actual_team_mon_in_pok2), 0)

    def test_merge_team_mons_into_mon1(self):
        # dummy examples
        team_mons_in_mon1 = pd.DataFrame(
            {
                "Format": ["[Gen 9] OU"],
                "Pokemon1": ["Pikachu"],
                "Pokemon2": ["Charizard"],
                "Winrate": [60],
                "SampleSize": [50],
            }
        )

        team_mons_in_mon2 = pd.DataFrame(
            {
                "Format": ["[Gen 9] OU"],
                "Pokemon1": ["Pikachu"],
                "Pokemon2": ["Bulbasaur"],
                "Winrate": [70],
                "SampleSize": [30],
            }
        )

        expected_result = pd.DataFrame(
            {
                "Format": ["[Gen 9] OU", "[Gen 9] OU"],
                "Pokemon1": ["Pikachu", "Bulbasaur"],  # Bulbasaur is now in Pokemon1
                "Pokemon2": ["Charizard", "Pikachu"],
                "Winrate": [60, 30],  # reverse Pikachu vs Bulbasaur winrate, 70-->30
                "SampleSize": [50, 30],
            }
        )

        actual_result = self.antimeta_calculator._merge_team_mons_into_mon1(
            team_mons_in_mon1, team_mons_in_mon2
        )

        pd.testing.assert_frame_equal(expected_result, actual_result, check_like=True)

    def test_get_presumed_winrate(self):
        self.mock_format_data.top30 = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Winrate": [60, 55, 45, 40],
            }
        )
        top30mon = "Pikachu"
        expected_winrate = 100 - 60  # 100 - Pikachu's winrate
        actual_winrate = self.antimeta_calculator._get_presumed_winrate(top30mon)
        self.assertEqual(expected_winrate, actual_winrate)

    def test_antimeta_winrate(self):
        team = [
            "Charizard",
            "Bulbasaur",
            "Squirtle",
        ]  # include Squirtle to test presumed winrate as total sample size will be <30

        """
        ----- MATH -----
        Charizard into top30 mons:
        1. Charizard vs Pikachu: 40 | SampleSize: 50
        2. Charizard vs Charizard: 50 | SampleSize: 20
        3. Charizard vs Bulbasaur: 90 | SampleSize: 15
        4. Charizard vs Squirtle: 55 | SampleSize: 5

        Bulbasaur into top30 mons:
        1. Bulbasaur vs Pikachu: 30 | SampleSize: 30
        2. Bulbasaur vs Charizard: 10 | SampleSize: 15
        3. Bulbasaur vs Bulbasaur: 50 | SampleSize: 10
        4. Bulbasaur vs Squirtle: 60 | SampleSize: 5

        Squirtle into top30 mons:
        1. Squirtle vs Pikachu: 20 | SampleSize: 5
        2. Squirtle vs Charizard: 45 | SampleSize: 5
        3. Squirtle vs Bulbasaur: 40 | SampleSize: 5
        4. Squirtle vs Squirtle: 50 | SampleSize: 5

        team winrates into top30 mons:
        1. team vs Pikachu: 40, 30, 20 = 30 | SampleSize: sufficient
        2. team vs Charizard: 50, 10, 45 = 35 | SampleSize: sufficient
        3. team vs Bulbasaur: 90, 50, 40 = 60 | SampleSize: sufficient
        4. team vs Squirtle: reverse overall = 60 | SampleSize: NOT sufficient
        """

        expected_result = pd.DataFrame(
            {
                "winrate": [
                    30.00,
                    35.00,
                    60.00,
                    60.00,  # Squirtle's presumed winrate
                ]
            },
            index=["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
        )

        actual_result = self.wr_calc._antimeta_winrate(team)

        print("\n\n")
        print(expected_result)
        print("\n\n")
        print(actual_result)
        print("\n\n")

        pd.testing.assert_frame_equal(expected_result, actual_result, check_like=True)


if __name__ == "__main__":
    unittest.main()
