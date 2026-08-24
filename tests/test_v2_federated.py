import unittest
import numpy as np
from studies.federated.digits_budget import assign,client_probabilities,entropy,proto_bytes
class V2FederatedTests(unittest.TestCase):
 def test_partition_and_bytes(self):
  rng=np.random.default_rng(1);p,_=client_probabilities(np.arange(10),5,.3,rng);y=np.tile(np.arange(10),20);c=assign(y,p,rng,True);self.assertEqual(len(c),len(y));self.assertEqual(set(c),set(range(5)));self.assertGreater(entropy(y),2);self.assertEqual(proto_bytes(2,64),600)
if __name__=='__main__':unittest.main()
