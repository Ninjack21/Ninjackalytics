import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from .team_classes import (
    WinrateCalculator,
    FormatData,
    CreativityRestrictor,
    TeamSolver,
    DisplayTeam,
)


# NOTE: for FormatData tests only right now
class MockDatabaseData:
    def __init__(self):
        super().__init__()

    def get_battle_info(self):
        return pd.DataFrame(
            {
                "Format": ["battle_format", "battle_format", "battle_format"],
                "P1_team": [1, 2, 3],
                "P2_team": [2, 3, 1],
            }
        )

    def get_teams(self):
        # Return the desired teams data
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "Pokemon1": ["Pikachu", "Charizard", "Bulbasaur"],
                "Pokemon2": ["Charizard", "Bulbasaur", "Squirtle"],
                "Pokemon3": ["Bulbasaur", "Squirtle", "Pikachu"],
            }
        )

    def get_pvpmetadata(self):
        # Return the desired pvpmetadata data
        return pd.DataFrame(
            {
                "Format": ["battle_format", "battle_format", "battle_format"],
                "Pokemon1": ["Pikachu", "Charizard", "Bulbasaur"],
                "Pokemon2": ["Charizard", "Bulbasaur", "Squirtle"],
                "Winrate": [60, 70, 80],
                "SampleSize": [50, 30, 5],
            }
        )

    def get_pokemonmetadata(self):
        # Return the desired pokemonmetadata data
        return pd.DataFrame(
            {
                "Format": [
                    "battle_format",
                    "battle_format",
                    "battle_format",
                    "battle_format",
                ],
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Popularity": [100, 50, 30, 20],
            }
        )


class TestFormatData(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDatabaseData()
        self.format_data = FormatData("battle_format", self.mock_db)

    def test_get_format_available_mons(self):
        # Mock the format_metadata DataFrame
        self.format_data.format_metadata = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "SampleSize": [100, 50, 30, 20],
            }
        )

        expected_mons = ["Pikachu", "Charizard", "Bulbasaur"]
        actual_mons = self.format_data.get_format_available_mons()

        self.assertEqual(actual_mons, expected_mons)


class TestCreativityRestrictor(unittest.TestCase):
    def setUp(self):
        self.mock_format_data = Mock()
        self.mock_format_data.format_metadata = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Popularity": [60, 55, 45, 12],
                "SampleSize": [100, 100, 100, 35],
            }
        )
        self.mock_format_data.top30 = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Popularity": [60, 55, 45, 40],
            }
        )
        self.creativity_restrictor = CreativityRestrictor(50, self.mock_format_data)

    def test_get_min_max_popularity(self):
        target_popularity = 50
        current_avg_popularity = 35
        remaining_slots = 2
        (
            min_popularity,
            max_popularity,
        ) = self.creativity_restrictor._get_min_max_popularity(
            target_popularity, remaining_slots, current_avg_popularity
        )
        # the math is a pain here so I'm going to recreate it manually to verify rather than typing it out
        # yes this will more or less mimic the code but the math is too annoying to do otherwise haha
        std = self.mock_format_data.top30["Popularity"].std()

        bound_range = std * 0.15 * remaining_slots

        calc_min_pop = (
            (target_popularity - bound_range) * 6
            - current_avg_popularity * (6 - remaining_slots)
        ) / remaining_slots
        calc_max_pop = (
            (target_popularity + bound_range) * 6
            - (current_avg_popularity * (6 - remaining_slots))
        ) / remaining_slots

        self.assertEqual(min_popularity, calc_min_pop)
        self.assertEqual(max_popularity, calc_max_pop)

    def test_get_target_avg_popularity(self):
        self.mock_format_data.top30 = pd.DataFrame(
            {"Popularity": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
        )
        self.creativity_restrictor.creativity = 50
        # 70th quantile = 73 | 50/100 creativity = 0.5*(73-10) = 31.5 | 73 - 31.5 = 41.5
        expected_target_avg_popularity = 73 - (50 / 100) * (73 - 10)
        actual_target_avg_popularity = (
            self.creativity_restrictor._get_target_avg_popularity()
        )
        self.assertEqual(expected_target_avg_popularity, actual_target_avg_popularity)

    def test_get_min_max_target_popularity(self):
        self.mock_format_data.top30 = pd.DataFrame(
            {"Popularity": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
        )
        (
            min_popularity,
            max_popularity,
        ) = self.creativity_restrictor._get_min_max_target_popularity()

        """
        Note on how pandas quantile works:
        The 70th quantile (or the 0.7 quantile) of a list or a DataFrame column is the value below which 70% 
        of the data fall.

        In your case, the list is [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]. The 70th quantile of this list is 70.

        The DataFrame.quantile(q) function in pandas calculates the q-th quantile of the DataFrame's data along the 
        specified axis. For a one-dimensional DataFrame or a single column of a DataFrame, this is equivalent to 
        sorting the data and selecting the value at index q * (n - 1), where n is the number of data points.

        In this case, the DataFrame has 10 data points, so the 70th quantile is the value 
        at index 0.7 * (10 - 1) = 6.3. Since this is not an integer, pandas interpolates between the values at 
        indices 6 and 7 to calculate the quantile. The values at these indices are 70 and 80, 
        so the 70th quantile is 70 + 0.3 * (80 - 70) = 73.
        """

        self.assertEqual(min_popularity, 10)
        self.assertEqual(max_popularity, 73)

    def test_define_popularity_bounds_for_available_pokemon(self):
        # ============== CASE WHERE CURRENT IS ABOVE TARGET AVG =================
        # ensure that as the remaining slots decreases, the min and max popularities also decrease
        remaining_slots = 5
        # no restriction initially
        (
            prev_min_popularity,
            prev_max_popularity,
        ) = self.creativity_restrictor._define_popularity_bounds_for_available_pokemon(
            current_avg_popularity=50,
            target_avg_popularity=30,
            remaining_slots=remaining_slots,
        )
        remaining_slots -= 1
        while remaining_slots >= 1:
            # assuming the same current avg popularity and target avg popularity, reducing remaining slots should
            # reduce or maintain the min and max popularities bounds returned
            (
                new_min_popularity,
                new_max_popularity,
            ) = self.creativity_restrictor._define_popularity_bounds_for_available_pokemon(
                current_avg_popularity=50,
                target_avg_popularity=30,
                remaining_slots=remaining_slots,
            )
            # min popularity should be decreasing or flat (to drive avg down)
            self.assertTrue(new_min_popularity <= prev_min_popularity)
            # max popularity should be decreasing or flat (to drive avg down)
            self.assertTrue(new_max_popularity <= prev_max_popularity)
            prev_min_popularity = new_min_popularity
            prev_max_popularity = new_max_popularity
            remaining_slots -= 1

        # ============== CASE WHERE CURRENT IS BELOW TARGET AVG =================
        # ensure that as the remaining slots decreases, the min and max popularities also decrease
        remaining_slots = 5
        # no restriction initially
        (
            prev_min_popularity,
            prev_max_popularity,
        ) = self.creativity_restrictor._define_popularity_bounds_for_available_pokemon(
            current_avg_popularity=20,
            target_avg_popularity=30,
            remaining_slots=remaining_slots,
        )
        remaining_slots -= 1
        while remaining_slots >= 1:
            # assuming the same current avg popularity and target avg popularity, reducing remaining slots should
            # reduce or maintain the min and max popularities bounds returned
            (
                new_min_popularity,
                new_max_popularity,
            ) = self.creativity_restrictor._define_popularity_bounds_for_available_pokemon(
                current_avg_popularity=20,
                target_avg_popularity=30,
                remaining_slots=remaining_slots,
            )
            # min popularity should be increasing or flat (to drive avg up)
            self.assertTrue(new_min_popularity >= prev_min_popularity)
            # max popularity should be increasing or flat (to drive avg up)
            self.assertTrue(new_max_popularity >= prev_max_popularity)
            prev_min_popularity = new_min_popularity
            prev_max_popularity = new_max_popularity
            remaining_slots -= 1

    def test_restrict_available_mons(self):
        # tool nearest 15 if less than 6 with idea that minimum pool I want to consider is 6 mons.
        # after removing current team, ensure this list has 6 remaining mons
        available_mons = [
            "Pikachu",
            "Charizard",
            "Bulbasaur",
            "Squirtle",
            "Mon1",
            "Mon2",
            "Mon3",
            "Mon4",
        ]
        # update format metadata to reflect above
        self.mock_format_data.format_metadata = pd.DataFrame(
            {
                "Pokemon": [
                    "Pikachu",
                    "Charizard",
                    "Bulbasaur",
                    "Squirtle",
                    "Mon1",
                    "Mon2",
                    "Mon3",
                    "Mon4",
                ],
                "Popularity": [60, 55, 45, 40, 35, 30, 25, 20],
                "SampleSize": [100, 100, 100, 35, 30, 25, 20, 15],
            }
        )

        current_team = ["Pikachu", "Charizard"]
        actual_available_mons = self.creativity_restrictor.restrict_available_mons(
            available_mons, current_team
        )
        # verify that at least 6 mons are present (per the logic of the calculator)
        self.assertGreaterEqual(len(actual_available_mons), 6)

        # ====== CASE WHERE CREATIVITY = 0 ======
        creativity_restrictor = CreativityRestrictor(0, self.mock_format_data)
        available_mons = ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"]
        current_team = ["Pikachu", "Charizard"]
        # with a creativity of 0 there should be no restrictions by popularity (but current team is excluded)
        expected_available_mons = ["Bulbasaur", "Squirtle"]
        actual_available_mons = creativity_restrictor.restrict_available_mons(
            available_mons, current_team
        )
        self.assertEqual(set(expected_available_mons), set(actual_available_mons))

    def test_restrict_mons_where_none_fit_bounds(self):
        """
        if we reach a point where no mons fit in the bounds provided then we should simply return the 10 mons
        nearest in popularity to the midpoint of the min/max popularity bounds provided
        """
        # create a new top30 with 16 mons (Pikachu + 15) all with very similar popularities
        self.mock_format_data.top30 = pd.DataFrame(
            {
                "Pokemon": [
                    "Pikachu",
                    "Charizard",
                    "Bulbasaur",
                    "Squirtle",
                    "Mew",
                    "Mewtwo",
                    "Rayquaza",
                    "Groudon",
                    "Kyogre",
                    "Lugia",
                    "Ho-oh",
                    "Giratina",
                    "Dialga",
                    "Palkia",
                    "Arceus",
                    "Zacian",
                ],
                "Popularity": [
                    60,
                    55,
                    45,
                    40,
                    45,
                    50,
                    45,
                    50,
                    55,
                    60,
                    55,
                    50,
                    45,
                    50,
                    55,
                    40,
                ],
            }
        )
        self.mock_format_data.format_metadata = pd.DataFrame(
            {
                "Pokemon": [
                    "Pikachu",
                    "Charizard",
                    "Bulbasaur",
                    "Squirtle",
                    "Mew",
                    "Mewtwo",
                    "Rayquaza",
                    "Groudon",
                    "Kyogre",
                    "Lugia",
                    "Ho-oh",
                    "Giratina",
                    "Dialga",
                    "Palkia",
                    "Arceus",
                    "Zacian",
                ],
                "Popularity": [
                    60,
                    55,
                    45,
                    40,
                    45,
                    50,
                    45,
                    50,
                    55,
                    60,
                    55,
                    50,
                    45,
                    50,
                    55,
                    40,
                ],
                "SampleSize": [
                    100,
                    100,
                    100,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                ],
            }
        )
        # now create a significant discrepancy in current_avg and target_avg to make the bounds at very low popularities
        # such that all of the above would normally be excluded
        creativity_restrictor = CreativityRestrictor(100, self.mock_format_data)

        available_mons = self.mock_format_data.top30["Pokemon"].tolist()
        current_team = ["Pikachu"]

        expected_available_mons = self.mock_format_data.top30["Pokemon"].tolist()
        expected_available_mons.remove("Pikachu")
        actual_available_mons = creativity_restrictor.restrict_available_mons(
            available_mons, current_team
        )
        self.assertEqual(set(expected_available_mons), set(actual_available_mons))

    def test_restrict_mons_where_available_mons_contain_subset_of_team(self):
        # ensure that Pikachu and Charizard-Cool are not returned as available
        available_mons = ["Pikachu", "Charizard-Cool", "Bulbasaur", "Squirtle"]
        current_team = ["Pikachu-Cool", "Charizard"]
        expected_available_mons = ["Bulbasaur", "Squirtle"]
        actual_available_mons = self.creativity_restrictor.restrict_available_mons(
            available_mons, current_team
        )
        self.assertEqual(set(expected_available_mons), set(actual_available_mons))


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
                "SampleSize": [50, 30, 5],
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

        pd.testing.assert_frame_equal(expected_result, actual_result, check_like=True)

    def test_normalized_winrate(self):
        team_winrates = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "winrate": [40.00, 50.00, 90.00, 55.00],
            }
        )

        """
        ----- MATH -----
        Pikachu popularity = 60
        Charizard popularity = 60
        Bulbasaur popularity = 60
        Squirtle popularity = 12

        Pikachu normalized winrate = 40 * (60/192) = 12.5
        Charizard normalized winrate = 50 * (60/192) = 15.625
        Bulbasaur normalized winrate = 90 * (60/192) = 28.125
        Squirtle normalized winrate = 55 * (12/192) = 3.4375

        sum = 59.6875
        """

        expected_result = 59.6875

        actual_result = self.wr_calc.normalized_winrate(team_winrates)

        self.assertAlmostEqual(expected_result, actual_result, places=4)


class TestTeamSolver(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDatabaseData()
        self.mock_format_data = Mock()
        self.mock_format_data.top30 = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur", "Squirtle"],
                "Popularity": [60, 55, 45, 40],
            }
        )
        self.team_solver = TeamSolver(db=self.mock_db, battle_format="OU")
        self.team_solver.format_data = self.mock_format_data

    def test_pick_random_top30_mon(self):
        # Call the method to test
        mon = self.team_solver._pick_random_top30_mon()
        # Check that the returned mon is in the top 30
        self.assertIn(mon, self.team_solver.format_data.top30["Pokemon"].values)

    @patch.object(WinrateCalculator, "get_team_winrate_against_meta")
    @patch.object(WinrateCalculator, "normalized_winrate")
    def test_choose_best_addition(
        self, mock_normalized_winrate, mock_get_team_winrate_against_meta
    ):
        # Set up the mock methods
        mock_normalized_winrate.side_effect = [0.5, 0.6]
        mock_get_team_winrate_against_meta.return_value = 0.5

        # Call the method to test
        available_mons = ["Bulbasaur", "Squirtle"]
        current_team = ["Pikachu", "Charizard"]
        current_norm_winrate = 0.5
        winrate_calculator = WinrateCalculator(
            format_data=self.mock_format_data, engine_name="antimeta"
        )
        best_mon = self.team_solver._choose_best_addition(
            available_mons, current_team, current_norm_winrate, winrate_calculator
        )

        # the last call to the normalized_winrate will be 0.6 which is better so Squirtle should be returned
        self.assertEqual(best_mon, "Squirtle")

    @patch.object(WinrateCalculator, "get_team_winrate_against_meta")
    @patch.object(WinrateCalculator, "normalized_winrate")
    @patch.object(CreativityRestrictor, "restrict_available_mons")
    def test_solve_for_remainder_of_team(
        self,
        mock_restrict_available_mons,
        mock_normalized_winrate,
        mock_get_team_winrate_against_meta,
    ):
        # ensure 4 new pokemon other than Bulba (in ignore mon) are present
        mock_restrict_available_mons.return_value = [
            "Bulbasaur",
            "Squirtle",
            "Pikachu",
            "Charizard",
            "Jigglypuff",
            "Meowth",
            "Psyduck",
        ]
        # just return 0.5 for everything: all improvements will be flat
        # this will cause the optimizer to always choose the first mon it looks at
        mock_normalized_winrate.return_value = 0.5
        mock_get_team_winrate_against_meta.return_value = 0.5

        # Call the method to test
        current_team = ["Pikachu", "Charizard"]
        creativity = 50
        ignore_mons = ["Bulbasaur"]
        engine_name = "antimeta"
        actual_team = self.team_solver.solve_for_remainder_of_team(
            current_team, creativity, ignore_mons, engine_name
        )

        # Check that the length of the returned team is 6
        self.assertEqual(len(actual_team), 6)


class TestDisplayTeam(unittest.TestCase):
    def setUp(self):
        self.team = ["Pikachu", "Charizard"]
        self.engine = "antimeta"
        self.format_data = MagicMock()
        self.format_data.top30 = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur"],
                "SampleSize": [100, 200, 150],
                "Format": ["format1", "format2", "format3"],
                "Winrate": [0.5, 0.6, 0.4],
                "Popularity": [0.5, 0.6, 0.4],
            }
        )
        self.format_data.format_metadata = pd.DataFrame(
            {
                "Pokemon": ["Pikachu", "Charizard", "Bulbasaur"],
                "Popularity": [0.5, 0.6, 0.4],
            }
        )
        self.display_team = DisplayTeam(self.team, self.engine, self.format_data)

    def test_get_avg_popularity(self):
        avg_popularity = self.display_team._get_avg_popularity()
        self.assertEqual(avg_popularity, 0.55)

    def test_add_meta_context_to_winrates(self):
        winrates = pd.DataFrame(
            {"Pokemon": ["Pikachu", "Charizard"], "winrate": [0.5, 0.6]}
        )
        context_df = self.display_team._add_meta_context_to_winrates(winrates)
        self.assertIsInstance(context_df, pd.DataFrame)
        self.assertEqual(context_df.shape[1], 4)  # 4 columns in the resulting DataFrame

    @patch.object(DisplayTeam, "_get_norm_winrate_and_winrates")
    def test_get_display_information(self, mock_get_norm_winrate_and_winrates):
        # Set up the mock method
        mock_get_norm_winrate_and_winrates.return_value = (
            0.75,
            pd.DataFrame(
                {
                    "Pokemon": ["Pikachu", "Charizard", "Bulbasaur"],
                    "winrate": [0.8, 0.7, 0.6],
                }
            ).set_index(
                "Pokemon"
            ),  # Set "Pokemon" as the index
        )

        # Call the method to test
        display_info = self.display_team.get_display_information()

        # Assertions
        self.assertIsInstance(display_info, dict)
        self.assertEqual(
            set(display_info.keys()),
            {"team", "avg_popularity", "norm_winrate", "team info"},
        )
        self.assertEqual(display_info["norm_winrate"], 0.75)


if __name__ == "__main__":
    unittest.main()
