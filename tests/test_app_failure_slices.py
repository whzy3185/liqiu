import unittest

from studies.application_slices.discovery import METHODS, evaluate_failure_slices


class ApplicationFailureSlicesTests(unittest.TestCase):
    def test_moons_end_to_end(self):
        result = evaluate_failure_slices("moons", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(0 <= row["coverage"] <= 1 for row in result["frontier"]))
        self.assertTrue(all(row["risk_uplift"] >= -1 for row in result["frontier"]))


if __name__ == "__main__":
    unittest.main()
