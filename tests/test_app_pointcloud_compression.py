import unittest

from studies.application_pointcloud.compression import METHODS, evaluate_pointcloud_compression


class ApplicationPointcloudCompressionTests(unittest.TestCase):
    def test_end_to_end(self):
        result = evaluate_pointcloud_compression("uniform", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(row["mean_chamfer"] >= 0 for row in result["frontier"]))
        self.assertEqual(len(result["frontier"]), len(METHODS) * 3)


if __name__ == "__main__":
    unittest.main()
