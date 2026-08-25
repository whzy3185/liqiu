import unittest

from studies.application_privacy.microaggregation import METHODS, evaluate_microaggregation


class ApplicationPrivacyMicroaggregationTests(unittest.TestCase):
    def test_wine_end_to_end(self):
        result = evaluate_microaggregation("wine", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(row["minimum_group_size"] >= row["k"] for row in result["frontier"]))
        self.assertTrue(all(row["distortion_mse"] >= 0 for row in result["frontier"]))


if __name__ == "__main__":
    unittest.main()
