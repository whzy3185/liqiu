import unittest
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from baselines.gbc import StableLocalPrunedGBC
class LocalPruningTests(unittest.TestCase):
 def test_pruned_interface(self):
  X,y=make_moons(n_samples=180,noise=.2,random_state=3);Xt,Xv,yt,yv=train_test_split(X,y,test_size=.3,stratify=y,random_state=3);m=StableLocalPrunedGBC(.5,min_validation=10).fit(Xt,yt,(Xv,yv));self.assertEqual(m.predict(Xv).shape,(54,));self.assertEqual(m.predict_proba(Xv).shape,(54,2));self.assertGreaterEqual(m.get_structure()['granule_count'],1)
if __name__=='__main__':unittest.main()
