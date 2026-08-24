import unittest

import numpy as np
from sklearn.model_selection import KFold

from studies.application_cleaning.cell_context import (
    METHODS,
    evaluate_cell_cleaning,
    inject_contextual_corruption,
)


class ApplicationCellCleaningTests(unittest.TestCase):
    def test_contextual_corruption_is_deterministic_and_bounded(self):
        values = np.random.default_rng(5).normal(size=(100, 6))
        folds = np.empty(100, dtype=int)
        for fold, (_, query) in enumerate(KFold(5, shuffle=True, random_state=9).split(values)):
            folds[query] = fold
        first, first_mask = inject_contextual_corruption(values, folds, 0.03, 11)
        second, second_mask = inject_contextual_corruption(values, folds, 0.03, 11)
        np.testing.assert_array_equal(first, second)
        np.testing.assert_array_equal(first_mask, second_mask)
        self.assertEqual(int(first_mask.sum()), round(0.03 * values.size))
        self.assertTrue(np.all(first[~first_mask] == values[~first_mask]))

    def test_wine_end_to_end(self):
        result = evaluate_cell_cleaning("wine", seed=3, corruption_rate=0.03, n_splits=3)
        self.assertEqual({row["method"] for row in result["methods"]}, set(METHODS))
        self.assertGreater(result["corrupted_cells"], 0)
        self.assertTrue(all(0 <= row["cell_auprc"] <= 1 for row in result["methods"]))


if __name__ == "__main__":
    unittest.main()
