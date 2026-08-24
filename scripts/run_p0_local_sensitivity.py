"""One bounded sensitivity check for P0 local validation sample floor."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(1489,'phoneme',5000),(151,'electricity',5000));SEEDS=(1,21,42);MINS=(5,10)
def generate():
 out=ROOT/'experiments/configs/candidates/p0_local_v2';out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for minimum in MINS:
   for seed in SEEDS:
    eid=f'p0lv2-{name}-m{minimum:02d}-s{seed}';cfg={'experiment_id':eid,'algorithm':'p0-stable-local-pruning-sensitivity','dataset':f'openml-{did}-{name}','dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},'pool':'exploration','seed':seed,'runner':'experiments.runners.p0_local_pruning:run','hyperparameters':{'cost_per_leaf':0,'min_validation':minimum},'search':{'enabled':False,'campaign':'p0_local_v2','bounded_sensitivity':True}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 18 P0 sensitivity configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/p0_local_v2').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);a=r.get('additional_metrics',{});print(i,18,r['experiment_id'],r['outcome'],a.get('accuracy_delta'),a.get('brier_delta'),r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
