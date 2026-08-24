"""Generate/run Candidate 4 conformal audit."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000));SEEDS=(1,21,42);ALPHAS=(.1,.2)
def generate():
 out=ROOT/'experiments/configs/candidates/c4_conformal_v1';out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for alpha in ALPHAS:
   for seed in SEEDS:
    eid=f'c4cv1-{name}-a{int(alpha*100):02d}-s{seed}';cfg={'experiment_id':eid,'algorithm':'c4-gbc-split-conformal-audit','dataset':f'openml-{did}-{name}','dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},'pool':'exploration','seed':seed,'runner':'experiments.runners.c4_conformal_audit:run','hyperparameters':{'alpha':alpha},'search':{'enabled':False,'campaign':'c4_conformal_v1','role':'novelty_and_utility_audit'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 30 Candidate 4 configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/c4_conformal_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);a=r.get('additional_metrics',{});g=a.get('gbc_conformal',{});f=a.get('rf_conformal',{});print(i,30,r['experiment_id'],r['outcome'],g.get('coverage'),g.get('average_set_size'),f.get('coverage'),f.get('average_set_size'),flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
