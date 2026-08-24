import unittest
import numpy as np
from sklearn.datasets import make_moons
from baselines.gbc import GranularBallClassifier
class CleanRoomGBCTests(unittest.TestCase):
 def test_interface_and_probabilities(self):
  X,y=make_moons(n_samples=100,noise=.1,random_state=1); model=GranularBallClassifier(.85).fit(X,y)
  self.assertEqual(model.predict(X).shape,(100,)); p=model.predict_proba(X)
  self.assertEqual(p.shape,(100,2)); np.testing.assert_allclose(p.sum(1),1)
  structure=model.get_structure(); self.assertEqual(len(structure['granules']),len(model.balls_)); self.assertIn('uncertainty',structure)
if __name__=='__main__': unittest.main()
