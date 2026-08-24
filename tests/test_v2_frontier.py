import unittest
from studies.risk_granularity.frontier import pareto_front,frontier_regret
from studies.risk_granularity.theory_harness import evaluate_configuration
class V2FrontierTests(unittest.TestCase):
 def test_pareto(self):
  p=pareto_front([{'cost':1,'risk':.4},{'cost':2,'risk':.5},{'cost':2,'risk':.2}]);self.assertEqual(len(p),2);self.assertTrue(any(x['risk']==.2 for x in p));self.assertEqual(len(frontier_regret(p,p)),2)
 def test_small_harness(self):
  r=evaluate_configuration({'family':'A','q':.7,'mixture_weight':.5,'n':120,'dimension':2,'noise':0},1,[.6,.8,1.0],[0,.01]);self.assertIn('oracle_frontier',r);self.assertGreaterEqual(r['max_granules'],r['granules'])
if __name__=='__main__':unittest.main()
