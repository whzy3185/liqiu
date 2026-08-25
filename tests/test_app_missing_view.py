import unittest

from studies.application_missingview.recovery import METHODS, evaluate_missing_view


class ApplicationMissingViewTests(unittest.TestCase):
    def test_wine_end_to_end(self):
        result = evaluate_missing_view("wine", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(row["imputation_nrmse"] >= 0 for row in result["frontier"]))
        self.assertEqual(len(result["frontier"]), len(METHODS) * 3)


if __name__ == "__main__":
    unittest.main()
