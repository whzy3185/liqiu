import unittest

from sklearn.datasets import make_classification

from secure_aggregation.compression import client_partitions, evaluate_prototypes, summarize_clients


class SecureAggregationTests(unittest.TestCase):
    def test_matched_counts_and_metrics(self):
        X, y = make_classification(n_samples=240, n_features=8, n_informative=6, random_state=7)
        partitions = client_partitions(y[:180], 5, 7)
        summaries = summarize_clients(X[:180], y[:180], partitions, 7, purity=0.85)
        self.assertEqual(len(summaries["granular_ball"].centers), len(summaries["kmeans"].centers))
        result = evaluate_prototypes(summaries["granular_ball"], X[180:], y[180:], 180)
        self.assertTrue(0 <= result["accuracy"] <= 1)
        self.assertGreater(result["communication_bytes"], 0)


if __name__ == "__main__":
    unittest.main()

