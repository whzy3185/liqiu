import unittest
import numpy as np
import scipy.sparse as sp
import pickle
from studies.graph_coarsening import coarsen_graph,heavy_edge_assignment,random_assignment,train_gcn,gbgc_adaptive_assignment,gbgc_fixed_ratio_assignment
class V2GNNTests(unittest.TestCase):
 def test_coarsening_and_gcn(self):
  rng=np.random.default_rng(1);X=sp.csr_matrix(rng.normal(size=(30,4)).astype('float32'));rows=np.r_[np.arange(29),np.arange(1,30)];cols=np.r_[np.arange(1,30),np.arange(29)];A=sp.csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(30,30));y=np.arange(30)%2;tr=np.arange(10);a=heavy_edge_assignment(A,20,1);self.assertEqual(a.max()+1,20);c=coarsen_graph(X,A,y,tr,a);r=train_gcn(c['features'],c['adjacency'],c['train_groups'],c['train_labels'],a,y,np.arange(10,20),np.arange(20,30),1,epochs=5,patience=3);self.assertIn('accuracy',r);self.assertEqual(random_assignment(30,10,1).max()+1,10)
 def test_cleanroom_gbgc_assignments(self):
  rows=np.r_[np.arange(19),np.arange(1,20)];cols=np.r_[np.arange(1,20),np.arange(19)];A=sp.csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(20,20));a,m=gbgc_adaptive_assignment(A);b,n=gbgc_fixed_ratio_assignment(A,.5);self.assertEqual(len(a),20);self.assertEqual(len(b),20);self.assertEqual(b.max()+1,10);self.assertIn('paper_deviations',m);self.assertIn('paper_deviations',n)
 def test_citeseer_reorder_matches_raw_test_labels(self):
  from studies.graph_coarsening import load_planetoid
  from pathlib import Path
  root=Path('work/planetoid')
  if not root.exists():self.skipTest('Planetoid cache unavailable')
  with (root/'ind.citeseer.ty').open('rb') as h:ty=pickle.load(h,encoding='latin1')
  test=np.array([int(x) for x in (root/'ind.citeseer.test.index').read_text().splitlines()]);data=load_planetoid(root,'citeseer');np.testing.assert_array_equal(np.argmax(ty,1),data['labels'][test])
if __name__=='__main__':unittest.main()
