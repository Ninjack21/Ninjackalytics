import unittest
from .team_analysis_funcs import get_team_winrates_against_top_30
import pandas as pd


class TestTeamAnalysisFuncs(unittest.TestCase):
    def test_get_team_winrates_against_top_30(self):
        # Create test data
        current_team = [
            "Pikachu",
            "Blaziken",
            "Swampert",
        ]  # Fill in the current team
        top30mons = [
            "Charizard",
            "Blastoise",
            "Venusaur",
        ]  # not really going to do 30 mons for testing
        format_pvp = pd.DataFrame(
            columns=["Pokemon1", "Pokemon2", "Winrate", "SampleSize"]
        )
        # going to have variable winrates with variable sample sizes
        format_pvp.loc[0] = ["Pikachu", "Charizard", 50, 100]  # 50 wins, 50 losses
        format_pvp.loc[1] = ["Pikachu", "Blastoise", 80, 50]  # 40 wins, 10 losses
        format_pvp.loc[2] = ["Pikachu", "Venusaur", 40, 200]  # 80 wins, 120 losses
        format_pvp.loc[3] = ["Blaziken", "Charizard", 50, 100]  # 50 wins, 50 losses
        format_pvp.loc[4] = ["Blaziken", "Blastoise", 30, 200]  # 60 wins, 140 losses
        format_pvp.loc[5] = ["Blaziken", "Venusaur", 90, 200]  # 180 wins, 20 losses
        format_pvp.loc[6] = ["Swampert", "Charizard", 80, 100]  # 80 wins, 20 losses
        format_pvp.loc[7] = ["Swampert", "Blastoise", 50, 100]  # 50 wins, 50 losses
        format_pvp.loc[8] = ["Swampert", "Venusaur", 20, 100]  # 20 wins, 80 losses

        """
        ---Calcs---
        Against Charizard = wins(50+50+80) / total(100+100+100) = (180/300) = 0.60
        Against Blastoise = wins(40+60+50) / total(50+200+100) = (150/350) = 0.43
        Against Venusaur = wins(80+180+20) / total(200+200+100) = (280/500) = 0.56
        """

        # Call the function
        result = get_team_winrates_against_top_30(current_team, top30mons, format_pvp)

        # Check the result
        self.assertAlmostEquals(result["winrate"].iloc[0], (180 / 300) * 100)
        self.assertAlmostEquals(result["winrate"].iloc[1], (150 / 350) * 100)
        self.assertAlmostEquals(result["winrate"].iloc[2], (280 / 500) * 100)

    def test_handle_finding_unique_combinations(self):
        """
        Not every pokemon exists in Pokemon1 and not every mon exists in Pokemon2, but all valid combinations are
        present. as such we need to handle the case where team_mon vs top30 mon is the reverse.
        """
        # Create test data
        current_team = [
            "Pikachu",
            "Blaziken",
            "Swampert",
        ]  # Fill in the current team
        top30mons = [
            "Charizard",
            "Blastoise",
            "Venusaur",
        ]  # not really going to do 30 mons for testing
        format_pvp = pd.DataFrame(
            columns=["Pokemon1", "Pokemon2", "Winrate", "SampleSize"]
        )
        # going to have variable winrates with variable sample sizes
        format_pvp.loc[0] = ["Pikachu", "Charizard", 50, 100]  # 50 wins, 50 losses
        # NOTE: Pikachu is now in Pokemon2, so wr is reversed
        format_pvp.loc[1] = ["Blastoise", "Pikachu", 20, 50]
        format_pvp.loc[2] = ["Pikachu", "Venusaur", 40, 200]  # 80 wins, 120 losses
        format_pvp.loc[3] = ["Blaziken", "Charizard", 50, 100]  # 50 wins, 50 losses
        format_pvp.loc[4] = ["Blaziken", "Blastoise", 30, 200]  # 60 wins, 140 losses
        format_pvp.loc[5] = ["Blaziken", "Venusaur", 90, 200]  # 180 wins, 20 losses
        format_pvp.loc[6] = ["Swampert", "Charizard", 80, 100]  # 80 wins, 20 losses
        format_pvp.loc[7] = ["Swampert", "Blastoise", 50, 100]  # 50 wins, 50 losses
        format_pvp.loc[8] = ["Swampert", "Venusaur", 20, 100]  # 20 wins, 80 losses

        """
        ---Calcs---
        Against Charizard = wins(50+50+80) / total(100+100+100) = (180/300) = 0.60
        Against Blastoise = wins(40+60+50) / total(50+200+100) = (150/350) = 0.43
        Against Venusaur = wins(80+180+20) / total(200+200+100) = (280/500) = 0.56
        """

        # Call the function
        result = get_team_winrates_against_top_30(current_team, top30mons, format_pvp)

        # Check the result
        self.assertAlmostEqual(result["winrate"].iloc[0], (180 / 300) * 100)
        self.assertAlmostEqual(result["winrate"].iloc[1], (150 / 350) * 100)
        self.assertAlmostEqual(result["winrate"].iloc[2], (280 / 500) * 100)


if __name__ == "__main__":
    unittest.main()
