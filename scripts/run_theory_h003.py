"""Generate/run minimal H-003 threshold incompatibility verification."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
REGIMES=('separable','uninformative');TAUS=(.6,.7,.8,.9);SEEDS=(1,7,21,42,2026)
def generate():
 out=ROOT/'experiments/configs/theory/h003_v1';out.mkdir(parents=True,exist_ok=True)
 for regime in REGIMES:
  for tau in TAUS:
   for seed in SEEDS:
    eid=f'th003v1-{regime}-p{int(tau*100):02d}-s{seed}';cfg={'experiment_id':eid,'algorithm':'cleanroom-original-gbc-theory-construction','dataset':f'h003-{regime}-q070','dataset_generation_parameters':{'regime':regime,'n_train':1000,'n_test':2000,'majority_probability':.7},'pool':'exploration','seed':seed,'runner':'experiments.runners.theory_h003_trial:run','hyperparameters':{'purity':tau},'search':{'enabled':False,'campaign':'theory_h003_v1'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 40 H-003 theory configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/theory/h003_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);print(i,40,r['experiment_id'],r['outcome'],r['accuracy'],r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
