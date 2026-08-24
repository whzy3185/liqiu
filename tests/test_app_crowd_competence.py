import unittest

import numpy as np

from studies.application_crowd.local_competence import (
    METHODS,
    evaluate_local_competence,
    fit_dawid_skene,
)


class ApplicationCrowdCompetenceTests(unittest.TestCase):
    def test_dawid_skene_shapes(self):
        annotations = np.array([[0, 0, 1], [1, 1, 1], [0, -1, 0], [1, 0, 1]])
        posterior, priors, confusion = fit_dawid_skene(annotations, 2)
        self.assertEqual(posterior.shape, (4, 2))
        self.assertEqual(priors.shape, (2,))
        self.assertEqual(confusion.shape, (3, 2, 2))
        np.testing.assert_allclose(posterior.sum(axis=1), 1.0)

    def test_moons_end_to_end(self):
        result = evaluate_local_competence("moons", "axis", 3, max_samples=400)
        self.assertEqual({row["method"] for row in result["methods"]}, set(METHODS))
        self.assertGreaterEqual(result["terminal_balls"], 1)
        for row in result["methods"]:
            self.assertTrue(0 <= row["aggregation_accuracy"] <= 1)
            self.assertTrue(0 <= row["competence_auprc"] <= 1)


if __name__ == "__main__":
    unittest.main()
