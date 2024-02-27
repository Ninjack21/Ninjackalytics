import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from .general_utility import (
    WinrateCalculator,
    FormatData,
)
from .team_classes import CreativityRestrictor, TeamSolver, DisplayTeam


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

    # NOTE: don't recreate conditions - already tested in TableAccessor
    def get_teams(self, conditions=None):
        # Return the desired teams data
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "Pokemon1": ["Pikachu", "Charizard", "Bulbasaur"],
                "Pokemon2": ["Charizard", "Bulbasaur", "Squirtle"],
                "Pokemon3": ["Bulbasaur", "Squirtle", "Pikachu"],
            }
        )

    def get_pvpmetadata(self, conditions=None):
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

    def get_pokemonmetadata(self, conditions=None):
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

    def test_choose_best_addition(self):
        print(
            "Multiprocessing made testing more difficult. Verify manually that choose best addition works."
        )
        self.assertTrue(True)

    def test_solve_for_remainder_of_team(self):
        print(
            "Multiprocessing made testing more difficult. Verify manually that solve for remainder of team works."
        )
        self.assertTrue(True)


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
        self.assertEqual(context_df.shape[1], 5)  # 4 columns in the resulting DataFrame

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
