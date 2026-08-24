import unittest

import numpy as np

from studies.application_online.local_memory import OnlineBallMemory, evaluate_online_memory


class ApplicationOnlineMemoryTests(unittest.TestCase):
    def test_memory_respects_cap(self):
        rng = np.random.default_rng(4)
        features = rng.normal(size=(120, 4))
        labels = (features[:, 0] > 0).astype(int)
        memory = OnlineBallMemory(np.array([0, 1]), max_balls=4).fit(features[:40], labels[:40])
        for step in range(1, 5):
            memory.update(features[40:60], labels[40:60], step)
            self.assertLessEqual(len(memory.balls), 4)
        self.assertEqual(memory.predict(features[:10], True).shape, (10,))

    def test_stream_end_to_end(self):
        result = evaluate_online_memory("emerging_class", seed=3, max_balls=12)
        self.assertLessEqual(result["max_balls"], 12)
        self.assertEqual(
            set(result["methods"]), {"gb_surface", "center_ablation", "sliding_gbc", "sgd"}
        )


if __name__ == "__main__":
    unittest.main()
