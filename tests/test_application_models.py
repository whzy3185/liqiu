import sys
import unittest
from pathlib import Path

import numpy as np
from sklearn.datasets import make_classification


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from applications.metrics import industrial_metrics
from applications.models import capped_fit_indices, conventional_models


class ApplicationModelTests(unittest.TestCase):
    def test_factory_contains_required_models(self):
        models = conventional_models(7, 2, class_counts={0: 90, 1: 10})
        names = {spec.name for spec in models}
        self.assertEqual(
            names,
            {"xgboost", "lightgbm", "catboost", "random_forest", "extra_trees", "knn", "svm_rbf"},
        )
        xgb = next(spec.estimator for spec in models if spec.name == "xgboost")
        self.assertEqual(xgb.get_params()["scale_pos_weight"], 9.0)

    def test_capped_indices_retain_both_classes(self):
        y = np.r_[np.zeros(990, dtype=int), np.ones(10, dtype=int)]
        indices = capped_fit_indices(y, 100, 7)
        self.assertLessEqual(len(indices), 100)
        self.assertEqual(set(y[indices]), {0, 1})

    def test_industrial_metrics_are_finite(self):
        X, y = make_classification(n_samples=100, n_classes=2, random_state=7)
        result = industrial_metrics(y, (X[:, 0] > np.median(X[:, 0])).astype(int))
        self.assertEqual(set(result), {"accuracy", "macro_f1", "balanced_accuracy", "mcc", "minority_recall", "g_mean"})
        self.assertTrue(np.isfinite(list(result.values())).all())


if __name__ == "__main__":
    unittest.main()
