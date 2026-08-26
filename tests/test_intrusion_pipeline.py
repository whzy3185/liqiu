import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

from applications.intrusion_tabular import load_unsw_nb15_screen


class IntrusionPipelineTests(unittest.TestCase):
    def test_loader_drops_direct_export_target_proxies(self):
        split=load_unsw_nb15_screen(7,str(ROOT/'data'/'intrusion'/'cache'/'openml'))
        forbidden={'id','Unnamed: 0','attack_cat','label'}
        self.assertFalse(forbidden & set(split.X_train.columns))
        self.assertEqual(set(split.y_train),{0,1})
        self.assertIn('diagnostic',split.protocol)


if __name__=='__main__': unittest.main()

