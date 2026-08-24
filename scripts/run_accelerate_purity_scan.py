"""Generate/run accelerated-GB cross-method purity scan."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000)); SEEDS=(1,21,42); PURITIES=(.60,.70,.80,.85,.90,.95,1.0); COMMIT='5986bea652f7e6e944af33572cc958cd096de5a1'
def generate():
 out=ROOT/'experiments/configs/real_validation/accelerate_purity_v1'; out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for purity in PURITIES:
   for seed in SEEDS:
    eid=f'purav1-{name}-p{int(round(purity*100)):03d}-s{seed}'; cfg={'experiment_id':eid,'algorithm':'author-accelerated-gbc-purity-scan','dataset':f'openml-{did}-{name}',
     'dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap},'pool':'exploration','seed':seed,'runner':'experiments.runners.real_accelerate_trial:run',
     'upstream_path':'work/upstreams/syxiaa_GBC/gb_accelerate_upload.py','upstream_commit':COMMIT,'hyperparameters':{'purity':purity},'search':{'enabled':True,'campaign':'accelerate_purity_v1'}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated',105,'accelerated purity configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}; paths=sorted((ROOT/'experiments/configs/real_validation/accelerate_purity_v1').glob('*.json'))
 for i,path in enumerate(paths,1):
  cfg=json.loads(path.read_text())
  if cfg['experiment_id'] in done: continue
  r=run_from_config(path,result); print(i,len(paths),r['experiment_id'],r['outcome'],r['accuracy'],r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
