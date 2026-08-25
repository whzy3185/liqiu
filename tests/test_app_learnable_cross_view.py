import unittest

from studies.application_learnable.cross_view import METHODS, evaluate_learnable_cross_view


class ApplicationLearnableCrossViewTests(unittest.TestCase):
    def test_wine_end_to_end(self):
        result = evaluate_learnable_cross_view("wine", 3, epochs=5)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(row["imputation_nrmse"] >= 0 for row in result["frontier"]))
        self.assertEqual(len(result["frontier"]), len(METHODS) * 3)


if __name__ == "__main__":
    unittest.main()
