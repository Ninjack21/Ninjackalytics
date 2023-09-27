import unittest

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)


def run_tests():
    test_dir = app_path + "/tests"
    test_pattern = "test_*.py"

    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=test_pattern)

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
