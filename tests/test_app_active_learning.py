import unittest

from studies.application_active.batch_query import METHODS, evaluate_batch_active_learning


class ApplicationActiveLearningTests(unittest.TestCase):
    def test_iris_end_to_end(self):
        result = evaluate_batch_active_learning("iris", seed=3)
        self.assertEqual({row["method"] for row in result["methods"]}, set(METHODS))
        for row in result["methods"]:
            self.assertTrue(0 <= row["accuracy_auc"] <= 1)
            self.assertTrue(all(0 <= point["accuracy"] <= 1 for point in row["curve"]))


if __name__ == "__main__":
    unittest.main()
