import json,unittest
from scripts.research_cycle import pending_configs,records
class ResearchCycleTests(unittest.TestCase):
 def test_all_existing_configs_have_unique_completed_ids_or_are_pending(self):
  ids=[r['experiment_id'] for r in records()];self.assertEqual(len(ids),len(set(ids)));self.assertIsInstance(pending_configs(),list)
if __name__=='__main__':unittest.main()
