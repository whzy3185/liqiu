import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from applications.finance_metrics import choose_validation_threshold, finance_metrics


class FinancePipelineTests(unittest.TestCase):
    def test_threshold_is_selected_from_validation_only(self):
        y = np.array([0, 0, 0, 1, 1])
        probability = np.array([0.02, 0.3, 0.4, 0.6, 0.9])
        threshold = choose_validation_threshold(y, probability)
        self.assertGreaterEqual(threshold, 0.01)
        metric = finance_metrics(y, probability, threshold)
        self.assertEqual(set(metric), {"pr_auc", "roc_auc", "macro_f1", "mcc", "recall_positive", "threshold"})
        self.assertTrue(np.isfinite(list(metric.values())).all())


if __name__ == "__main__":
    unittest.main()

