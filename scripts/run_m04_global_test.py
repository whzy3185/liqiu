"""Generate/run M04 global calibration negative control."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000)); SEEDS=(1,21,42); LAMBDAS=(0,.02,.10)
def generate():
 out=ROOT/'experiments/configs/candidates/m04_global_v1'; out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for lam in LAMBDAS:
   for seed in SEEDS:
    eid=f'm04gv1-{name}-l{int(round(lam*100)):02d}-s{seed}'; cfg={'experiment_id':eid,'algorithm':'m04-global-brier-cost-control','dataset':f'openml-{did}-{name}','dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},
     'pool':'exploration','seed':seed,'runner':'experiments.runners.m04_global_calibration:run','hyperparameters':{'ball_cost_lambda':lam},'search':{'enabled':False,'campaign':'m04_global_v1','role':'negative_control'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 45 M04 configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/m04_global_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done: continue
  r=run_from_config(path,result); a=r.get('additional_metrics',{}); print(i,45,r['experiment_id'],r['outcome'],a.get('selected_purity'),a.get('brier_delta_vs_fixed'),a.get('accuracy_delta_vs_fixed'),r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
