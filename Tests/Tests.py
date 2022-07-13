import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Project.core


class test_Weco(unittest.TestCase):
    test_weco = Project.core.WECO(
        data=pd.read_csv("Tests/TestData.csv", nrows=750, header=0),
        variable_name="Height",
    )

    def test_input_var(self):
        self.assertEqual(self.test_weco.variable_name, "Height")
        self.assertEqual(self.test_weco.applyrules, ["1", "2", "3", "4", "5", "6", "7", "8"])

    def test_av(self):
        self.assertEqual(self.test_weco.av, 68.94701)

    def test_std(self):
        self.assertEqual(self.test_weco.std, 2.80248)

    def test_violations(self):
        self.assertEqual(
            self.test_weco.ViolationsCSV(),
            [
                [566, 62.5, "2"],
                [567, 67.8, "2"],
                [194, 72.5, "3"],
                [195, 72.3, "3"],
                [197, 75.9, "3"],
                [207, 65.9, "3"],
                [597, 62.0, "3"],
                [143, 67.4, "4"],
                [146, 71.3, "5"],
                [534, 75.0, "5"],
                [110, 69.3, "6"],
                [111, 68.2, "6"],
                [112, 71.6, "6"],
                [113, 69.2, "6"],
                [114, 67.3, "6"],
                [727, 63.4, "7"],
                [728, 68.4, "7"],
                [729, 67.4, "7"],
                [730, 70.8, "7"],
                [731, 67.1, "7"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
