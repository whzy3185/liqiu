"""Generate/run streaming rebuild and online controls."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
KINDS=('covariate_shift','concept_drift','prior_shift','density_drift','emerging_class','disappearing_class');STRATEGIES=('no_update','full_rebuild','sliding_rebuild','sgd_online');SEEDS=(1,7,21)
def generate():
 out=ROOT/'experiments/configs/streaming/baseline_v1';out.mkdir(parents=True,exist_ok=True)
 for kind in KINDS:
  for strategy in STRATEGIES:
   for seed in SEEDS:
    eid=f'strv1-{kind}-{strategy}-s{seed}';cfg={'experiment_id':eid,'algorithm':f'stream-{strategy}','dataset':f'synthetic-stream-{kind}-v1','dataset_generation_parameters':{'kind':kind,'n_steps':10,'samples_per_step':200,'ambient_dimension':5,'drift_strength':2.0},'pool':'exploration','seed':seed,'runner':'experiments.runners.stream_baseline:run','hyperparameters':{'strategy':strategy},'search':{'enabled':False,'campaign':'stream_baseline_v1'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 72 stream baseline configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/streaming/baseline_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);print(i,72,r['experiment_id'],r['outcome'],r['accuracy'],r['runtime_seconds'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
