import unittest

import numpy as np

from studies.application_drift.sketch import (
    SHIFT_KINDS,
    evaluate_drift_sketches,
    fit_granular_ball_sketch,
    fit_kmeans_sketch,
)


class ApplicationDriftSketchTests(unittest.TestCase):
    def test_sketch_shapes_and_memory(self):
        points = np.random.default_rng(4).normal(size=(120, 4))
        for fitter in (fit_granular_ball_sketch, fit_kmeans_sketch):
            sketch = fitter(points, 8, 4)
            self.assertEqual(sketch.centers.shape, (8, 4))
            self.assertEqual(sketch.radii.shape, (8,))
            self.assertAlmostEqual(float(sketch.weights.sum()), 1.0)
            self.assertTrue(np.isfinite(sketch.score(points[:20])))
            self.assertEqual(sketch.memory_bytes, 8 * (8 * 4 + 8 + 8))

    def test_all_shift_kinds_run(self):
        for shift in SHIFT_KINDS:
            rows = evaluate_drift_sketches(
                shift,
                seed=3,
                dimension=4,
                reference_size=120,
                batch_size=30,
                budgets=(4,),
                severities=(0.5, 1.0),
                calibration_batches=4,
                repeats=3,
            )
            self.assertEqual({row["method"] for row in rows}, {
                "granular_ball", "kmeans", "reservoir_mmd", "full_mmd"
            })
            self.assertTrue(all(0 <= row["auroc"] <= 1 for row in rows))


if __name__ == "__main__":
    unittest.main()
