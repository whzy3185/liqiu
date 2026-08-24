import unittest
import numpy as np
from studies.granular_ball_core import fit_tree_frontier,classification_metrics
class GBCoreStressTests(unittest.TestCase):
 def test_two_tree_methods(self):
  rng=np.random.default_rng(1);X=rng.normal(size=(80,2));y=(X[:,0]>0).astype(int)
  for method in ('kmeans','class_means'):
   rows=fit_tree_frontier(X,y,X,y,method,1,taus=(.6,.85,1.));self.assertEqual(len(rows),3);self.assertGreaterEqual(rows[-1]['granules'],rows[0]['granules']);self.assertIn('selective',rows[0])
 def test_metrics(self):
  p=np.array([[.9,.1],[.2,.8]]);m=classification_metrics(np.array([0,1]),p);self.assertEqual(m['accuracy'],1);self.assertIn('brier',m)
if __name__=='__main__':unittest.main()
