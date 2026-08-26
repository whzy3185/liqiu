import sys
import unittest
from pathlib import Path

import numpy as np
from sklearn.datasets import make_blobs


ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gb_application.unsupervised import MatchedKMeansRegions, RecursiveBallCover, UNSUPERVISED_FEATURE_NAMES, uniform_fit_subset, unsupervised_features


class UnsupervisedLocalStructureTests(unittest.TestCase):
 def test_ball_and_kmeans_feature_schema_match(self):
  X,_=make_blobs(n_samples=300,centers=4,random_state=7)
  ball=RecursiveBallCover(max_regions=16,min_samples=10,random_state=7).fit(X)
  km=MatchedKMeansRegions(len(ball.regions_),random_state=7).fit(X)
  self.assertEqual(len(ball.regions_),len(km.centers_))
  self.assertEqual(unsupervised_features(ball,X).shape,(300,len(UNSUPERVISED_FEATURE_NAMES)))
  self.assertTrue(np.isfinite(unsupervised_features(km,X)).all())
 def test_uniform_cap_is_label_free_and_deterministic(self):
  a=uniform_fit_subset(1000,100,7);b=uniform_fit_subset(1000,100,7)
  np.testing.assert_array_equal(a,b);self.assertEqual(len(a),100)


if __name__=='__main__':unittest.main()

