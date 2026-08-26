import sys
import unittest
from pathlib import Path

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gb_application import STRUCTURAL_FEATURE_NAMES, cross_fitted_gb_features
from gb_application.models import append_gb_features


class CrossFitNoLeakageTests(unittest.TestCase):
    def setUp(self):
        X, y = make_classification(
            n_samples=360,
            n_features=12,
            n_informative=8,
            n_redundant=2,
            weights=[0.7, 0.3],
            random_state=7,
        )
        X_train, X_test, y_train, self.y_test = train_test_split(
            X, y, test_size=0.25, stratify=y, random_state=7
        )
        X_train, X_validation, y_train, self.y_validation = train_test_split(
            X_train, y_train, test_size=0.2, stratify=y_train, random_state=7
        )
        scaler = StandardScaler().fit(X_train)
        self.X_train = scaler.transform(X_train)
        self.X_validation = scaler.transform(X_validation)
        self.X_test = scaler.transform(X_test)
        self.y_train = y_train

    def test_oof_fit_and_query_indices_are_disjoint(self):
        result = cross_fitted_gb_features(
            self.X_train,
            self.y_train,
            self.X_validation,
            self.X_test,
            seed=7,
        )
        observed_queries = set()
        for audit in result.audits:
            self.assertFalse(set(audit.fit_indices) & set(audit.query_indices))
            observed_queries.update(audit.query_indices)
        self.assertEqual(observed_queries, set(range(len(self.X_train))))
        self.assertEqual(result.train.shape, (len(self.X_train), len(STRUCTURAL_FEATURE_NAMES)))
        self.assertEqual(result.validation.shape[0], len(self.X_validation))
        self.assertEqual(result.test.shape[0], len(self.X_test))
        self.assertTrue(np.isfinite(result.train).all())

    def test_query_features_do_not_accept_query_labels(self):
        result = cross_fitted_gb_features(
            self.X_train,
            self.y_train,
            self.X_validation,
            self.X_test,
            seed=21,
        )
        self.assertEqual(result.test.shape[1], 12)
        augmented = append_gb_features(self.X_train, result.train)
        self.assertEqual(augmented.shape[1], self.X_train.shape[1] + 12)

    def test_generator_fit_cap_stays_inside_oof_fit(self):
        result = cross_fitted_gb_features(
            self.X_train,
            self.y_train,
            self.X_validation,
            self.X_test,
            seed=42,
            generator_fit_cap=80,
        )
        self.assertEqual(result.full_fit_count, 80)
        for audit in result.audits:
            self.assertLessEqual(len(audit.fit_indices), 80)
            self.assertFalse(set(audit.fit_indices) & set(audit.query_indices))


if __name__ == "__main__":
    unittest.main()
