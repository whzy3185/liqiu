import unittest

import numpy as np

from counterexamples.generators import FAMILIES, generate


class GeneratorTests(unittest.TestCase):
    def test_all_families_shape_and_labels(self):
        self.assertGreaterEqual(len(FAMILIES), 10)
        for family in FAMILIES:
            X, y, metadata = generate(family, n_samples=120, seed=7)
            self.assertEqual(X.shape, (120, 2), family)
            self.assertEqual(y.shape, (120,), family)
            self.assertEqual(set(np.unique(y)), {0, 1}, family)
            self.assertEqual(metadata["family"], family)

    def test_deterministic_and_high_dimensional(self):
        first = generate("spirals", n_samples=101, seed=21, ambient_dimension=20, noise_rate=0.1, label_noise="boundary")
        second = generate("spirals", n_samples=101, seed=21, ambient_dimension=20, noise_rate=0.1, label_noise="boundary")
        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_array_equal(first[1], second[1])
        self.assertEqual(first[0].shape, (101, 20))
        self.assertEqual(first[2], second[2])


if __name__ == "__main__":
    unittest.main()
