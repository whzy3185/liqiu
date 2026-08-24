"""Generate/run M12 change-point heuristic red-team."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000)); SEEDS=(1,21,42); RULES=('knee','curvature','plateau_1pct')
def generate():
 out=ROOT/'experiments/configs/candidates/m12_v1'; out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for rule in RULES:
   for seed in SEEDS:
    eid=f'm12v1-{name}-{rule}-s{seed}'; cfg={'experiment_id':eid,'algorithm':'m12-purity-path-change-point','dataset':f'openml-{did}-{name}','dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},
     'pool':'exploration','seed':seed,'runner':'experiments.runners.m12_change_point:run','hyperparameters':{'change_rule':rule},'search':{'enabled':False,'campaign':'m12_v1','role':'heuristic_red_team'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 45 M12 configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/m12_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done: continue
  r=run_from_config(path,result); a=r.get('additional_metrics',{}); print(i,45,r['experiment_id'],r['outcome'],a.get('selected_purity'),a.get('accuracy_delta_vs_fixed'),r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
