import unittest
import numpy as np
from sklearn.datasets import make_moons
from baselines.gbc import ConfidenceBoundGranularBallClassifier,GranularBallClassifier
class CleanRoomGBCTests(unittest.TestCase):
 def test_interface_and_probabilities(self):
  X,y=make_moons(n_samples=100,noise=.1,random_state=1); model=GranularBallClassifier(.85).fit(X,y)
  self.assertEqual(model.predict(X).shape,(100,)); p=model.predict_proba(X)
  self.assertEqual(p.shape,(100,2)); np.testing.assert_allclose(p.sum(1),1)
  structure=model.get_structure(); self.assertEqual(len(structure['granules']),len(model.balls_)); self.assertIn('uncertainty',structure)
 def test_confidence_lower_bound_is_no_less_conservative(self):
  X,y=make_moons(n_samples=160,noise=.2,random_state=7)
  observed=GranularBallClassifier(.85).fit(X,y); bounded=ConfidenceBoundGranularBallClassifier(.85).fit(X,y)
  self.assertGreaterEqual(len(bounded.balls_),len(observed.balls_))
if __name__=='__main__': unittest.main()
