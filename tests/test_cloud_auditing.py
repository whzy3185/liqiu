import unittest

import numpy as np

from cloud_auditing.simulation import audit_policies, corruption_indices, evaluate_policy, generate_blocks


class CloudAuditingTests(unittest.TestCase):
    def test_policies_are_normalized_and_budget_is_fixed(self):
        blocks = generate_blocks(600, 7)
        policies, group_count = audit_policies(blocks, 7, fit_cap=400)
        self.assertGreaterEqual(group_count, 2)
        for policy in policies.values():
            self.assertEqual(policy.shape, (600,))
            self.assertAlmostEqual(float(policy.sum()), 1.0)
        corrupted = corruption_indices(blocks, "clustered", 20, 7)
        result = evaluate_policy(policies["granular_ball"], corrupted, 40, 7, repeats=5)
        self.assertEqual(result["audit_cost"], 40)
        self.assertTrue(0 <= result["detection_probability"] <= 1)

    def test_adversary_targets_policy_bottom(self):
        blocks = generate_blocks(500, 11)
        policy = np.arange(1, 501, dtype=float)
        policy /= policy.sum()
        corrupted = corruption_indices(blocks, "adversarial", 20, 11, policy)
        self.assertLessEqual(policy[corrupted].max(), np.quantile(policy, 0.2))


if __name__ == "__main__":
    unittest.main()

