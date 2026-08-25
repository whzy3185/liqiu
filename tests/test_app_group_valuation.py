import unittest

from studies.application_valuation.group_influence import METHODS, evaluate_group_influence


class ApplicationGroupValuationTests(unittest.TestCase):
    def test_wine_end_to_end(self):
        result = evaluate_group_influence("wine", 3)
        self.assertEqual({row["method"] for row in result["methods"]}, set(METHODS))
        self.assertTrue(all(-1 <= row["spearman_exact_influence"] <= 1 for row in result["methods"]))
        self.assertLess(max(row["retrains"] for row in result["methods"]), result["exact_retrains"])


if __name__ == "__main__":
    unittest.main()
