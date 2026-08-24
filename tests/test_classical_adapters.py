import unittest
import numpy as np
from sklearn.datasets import make_blobs
from baselines.classical_ml import AdaBoostAdapter,DBSCANAdapter,KMeansAdapter,KNNAdapter,RandomForestAdapter,SVMAdapter
class ClassicalAdapterTests(unittest.TestCase):
 def test_classifier_interfaces(self):
  X,y=make_blobs(n_samples=80,centers=2,random_state=1)
  for model in (KNNAdapter(n_neighbors=3),SVMAdapter(random_state=1),RandomForestAdapter(n_estimators=10,random_state=1),AdaBoostAdapter(n_estimators=10,random_state=1)):
   model.fit(X,y);self.assertEqual(model.predict(X).shape,(80,));self.assertEqual(model.predict_proba(X).shape,(80,2));self.assertIn('type',model.get_structure())
 def test_cluster_interfaces(self):
  X,_=make_blobs(n_samples=80,centers=2,random_state=1)
  for model in (KMeansAdapter(2),DBSCANAdapter(eps=1.5,min_samples=3)):
   model.fit(X,None);self.assertEqual(model.predict(X).shape,(80,));self.assertEqual(model.predict_proba(X).shape[0],80);self.assertIn('members',model.get_structure())
if __name__=='__main__':unittest.main()
