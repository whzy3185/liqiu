"""Generate/run preregistered H-003 confirmation without tuning."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
DATASETS=((44,'spambase',4601),(1494,'qsar-biodeg',1055),(1479,'hill-valley',1212));SEEDS=(1,7,21,42,2026);PURITIES=(.70,.85,1.0);COMMIT='5986bea652f7e6e944af33572cc958cd096de5a1'
def generate():
 out=ROOT/'experiments/configs/confirmation/h003_v1';out.mkdir(parents=True,exist_ok=True)
 rationale='Preregistered H-003 fixed-condition confirmation; no threshold selection or tuning.'
 for did,name,cap in DATASETS:
  for method in ('original','accelerated'):
   for purity in PURITIES:
    for seed in SEEDS:
     eid=f'confh003-{name}-{method}-p{int(purity*100):03d}-s{seed}';common={'experiment_id':eid,'algorithm':f'confirmation-{method}-gbc-purity-path','dataset':f'openml-{did}-{name}','dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},'pool':'confirmation','confirmation_rationale':rationale,'seed':seed,'hyperparameters':{'purity':purity},'search':{'enabled':False},'claim_validation':True}
     if method=='original':common['runner']='experiments.runners.real_gbc_trial:run'
     else:common.update({'runner':'experiments.runners.real_accelerate_trial:run','upstream_path':'work/upstreams/syxiaa_GBC/gb_accelerate_upload.py','upstream_commit':COMMIT})
     (out/f'{eid}.json').write_text(json.dumps(common,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 90 preregistered confirmation configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/confirmation/h003_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);print(i,90,r['experiment_id'],r['outcome'],r['accuracy'],r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
