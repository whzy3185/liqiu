import unittest

from studies.application_sensor.placement import METHODS, evaluate_sensor_placement


class ApplicationSensorPlacementTests(unittest.TestCase):
    def test_end_to_end(self):
        result = evaluate_sensor_placement("anisotropic", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(row["normalized_rmse"] >= 0 for row in result["frontier"]))
        self.assertEqual(len(result["frontier"]), len(METHODS) * 3)


if __name__ == "__main__":
    unittest.main()
