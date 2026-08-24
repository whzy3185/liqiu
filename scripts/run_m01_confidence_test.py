"""Cheap kill test for one-sided Wilson lower-bound purity stopping."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000)); SEEDS=(1,21,42)
def generate():
 out=ROOT/'experiments/configs/candidates/m01_v1'; out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for seed in SEEDS:
   eid=f'm01v1-{name}-s{seed}'; cfg={'experiment_id':eid,'algorithm':'m01-wilson-lower-purity-stop','dataset':f'openml-{did}-{name}',
    'dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},'pool':'exploration','seed':seed,'runner':'experiments.runners.real_gbc_trial:run',
    'hyperparameters':{'purity':.85,'stop_rule':'wilson_lower'},'search':{'enabled':False,'campaign':'m01_v1'}}
   (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 15 M01 configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/m01_v1').glob('*.json')),1):
  cfg=json.loads(path.read_text())
  if cfg['experiment_id'] in done: continue
  r=run_from_config(path,result); print(i,15,r['experiment_id'],r['outcome'],r['accuracy'],r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
