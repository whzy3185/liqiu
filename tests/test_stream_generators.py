import unittest
import numpy as np
from counterexamples.generators import STREAM_KINDS,generate_stream
class StreamGeneratorTests(unittest.TestCase):
 def test_all_streams_and_replay(self):
  self.assertEqual(len(STREAM_KINDS),6)
  for kind in STREAM_KINDS:
   a=generate_stream(kind,n_steps=6,samples_per_step=40,seed=7,ambient_dimension=5);b=generate_stream(kind,n_steps=6,samples_per_step=40,seed=7,ambient_dimension=5)
   self.assertEqual(a[0].shape,(240,5));self.assertEqual(a[1].shape,(240,));self.assertEqual(set(a[2]),set(range(6)));np.testing.assert_array_equal(a[0],b[0]);np.testing.assert_array_equal(a[1],b[1]);self.assertEqual(a[3],b[3])
 def test_emerging_class_appears_late(self):
  _,y,t,_=generate_stream('emerging_class',n_steps=6,samples_per_step=100,seed=1);self.assertNotIn(2,set(y[t<3]));self.assertIn(2,set(y[t>=3]))
if __name__=='__main__':unittest.main()
