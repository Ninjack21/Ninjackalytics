import os

os.environ["FLASK_ENV"] = "testing"

import unittest
import pandas as pd
from unittest.mock import patch
from .update_metadata_tables import (
    update_metadata,
    contains_mon,
    get_rank_limit_based_on_quantile,
    upload_new_data,
    update_no_longer_seen_mons,
)


# TODO: hook up to testing db and run tests to verify math working as expected
class TestUpdateMetaDataTables(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test data or configurations
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    def test_contains_mon(self):
        # Test the contains_mon function
        row = pd.Series(["mon1", "mon2", "mon3"])
        self.assertTrue(contains_mon(row, "mon1"))
        self.assertFalse(contains_mon(row, "mon4"))

    def test_get_rank_limit_based_on_quantile(self):
        # Test the get_rank_limit_based_on_quantile function
        battle_info = pd.DataFrame({"Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        rank_limit = get_rank_limit_based_on_quantile(battle_info)
        self.assertEqual(rank_limit, 7)


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
