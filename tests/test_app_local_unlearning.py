import unittest

from studies.application_unlearning.local_delete import METHODS, SCENARIOS, evaluate_local_unlearning


class ApplicationLocalUnlearningTests(unittest.TestCase):
    def test_wine_end_to_end(self):
        result = evaluate_local_unlearning("wine", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertEqual({row["scenario"] for row in result["frontier"]}, set(SCENARIOS))
        self.assertTrue(all(0 <= row["agreement_with_full_retrain"] <= 1 for row in result["frontier"]))


if __name__ == "__main__":
    unittest.main()
