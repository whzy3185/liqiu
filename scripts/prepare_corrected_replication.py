"""Create v2 configs after correcting nearest-center to boundary distance."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
def migrate(source_name,target_name,old_prefix,new_prefix):
 source=ROOT/'experiments/configs/failure_search'/source_name; target=ROOT/'experiments/configs/failure_search'/target_name; target.mkdir(parents=True,exist_ok=True)
 for path in sorted(source.glob('*.json')):
  cfg=json.loads(path.read_text()); cfg['experiment_id']=cfg['experiment_id'].replace(old_prefix,new_prefix,1)
  cfg['dataset']=cfg['dataset'].replace('v1','v2'); cfg['search']['campaign']=target_name; cfg['search']['prediction_distance']='center_norm_minus_mean_radius'
  (target/f"{cfg['experiment_id']}.json").write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(target_name,len(list(target.glob('*.json'))))
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; completed={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 paths=sorted((ROOT/'experiments/configs/failure_search/xor_v2').glob('*.json'))+sorted((ROOT/'experiments/configs/failure_search/alternating_v2').glob('*.json'))
 for i,path in enumerate(paths,1):
  cfg=json.loads(path.read_text())
  if cfg['experiment_id'] in completed: continue
  r=run_from_config(path,result); print(i,len(paths),r['experiment_id'],r['outcome'],r.get('additional_metrics',{}).get('accuracy_gap'),flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:
  migrate('xor_v1','xor_v2','xorv1','xorv2'); migrate('alternating_v1','alternating_v2','altv1','altv2')
 if '--generate-only' not in sys.argv: run()
