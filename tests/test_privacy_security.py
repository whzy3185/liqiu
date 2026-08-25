import unittest

import numpy as np
from sklearn.datasets import make_classification

from privacy_security.evaluation import evaluate_release
from privacy_security.summaries import all_releases


class PrivacySecurityTests(unittest.TestCase):
    def test_releases_and_metrics_are_complete(self):
        X, y = make_classification(
            n_samples=180,
            n_features=7,
            n_informative=5,
            random_state=7,
        )
        sensitive = (X[:, -1] > np.median(X[:, -1])).astype(int)
        releases = all_releases(X[:90], y[:90], seed=7, purity=0.85)
        variants = {release.variant[:3] for release in releases}
        self.assertTrue({f"R{i}_" for i in range(9)} <= variants)
        gb = next(release for release in releases if release.variant == "R8_center_radius_count_purity")
        km = next(release for release in releases if release.variant == "R4_center_radius_count")
        self.assertEqual(len(gb.centers), len(km.centers))
        result = evaluate_release(
            gb,
            X[:90],
            y[:90],
            X[90:],
            y[90:],
            sensitive[:90],
            6,
            seed=7,
        )
        self.assertTrue(0 <= result["membership_roc_auc"] <= 1)
        self.assertTrue(0 <= result["utility_accuracy"] <= 1)


if __name__ == "__main__":
    unittest.main()

