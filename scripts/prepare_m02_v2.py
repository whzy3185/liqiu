"""Create and run corrected M02 configs with new immutable experiment IDs."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
def generate():
 source=ROOT/'experiments/configs/candidates/m02_global_v1'; target=ROOT/'experiments/configs/candidates/m02_global_v2'; target.mkdir(parents=True,exist_ok=True)
 for path in source.glob('*.json'):
  c=json.loads(path.read_text()); c['experiment_id']=c['experiment_id'].replace('m02gv1','m02gv2',1); c['search']['campaign']='m02_global_v2'; c['search']['corrects']='double-scaled-test bug in v1'
  (target/f"{c['experiment_id']}.json").write_text(json.dumps(c,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated',len(list(target.glob('*.json'))),'M02 v2 configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/m02_global_v2').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done: continue
  r=run_from_config(path,result); a=r.get('additional_metrics',{}); print(i,45,r['experiment_id'],r['outcome'],a.get('selected_purity'),a.get('accuracy_delta_vs_fixed'),r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
