import unittest

from multi_auditor.simulation import evaluate_methods, generate_world


class MultiAuditorTests(unittest.TestCase):
    def test_all_required_methods_and_metrics(self):
        world = generate_world(20, 0.2, 0.8, 0.1, 7, n_history=80, n_current=100)
        rows = evaluate_methods(world, 7)
        methods = {row["method"] for row in rows}
        self.assertTrue({"dawid_skene", "knn_competence", "granular_ball", "gb_three_way"} <= methods)
        for row in rows:
            self.assertTrue(0 <= row["metrics"]["final_audit_accuracy"] <= 1)


if __name__ == "__main__":
    unittest.main()

