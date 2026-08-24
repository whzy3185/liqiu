"""Scan fixed purity across public datasets to test one-rule adequacy."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
DATASETS=((59,'ionosphere',351),(40,'sonar',208),(1462,'banknote-authentication',1372),(1489,'phoneme',5000),(151,'electricity',5000)); SEEDS=(1,21,42); PURITIES=(.60,.70,.80,.85,.90,.95,1.0)
def generate():
 out=ROOT/'experiments/configs/real_validation/purity_v1'; out.mkdir(parents=True,exist_ok=True)
 for did,name,cap in DATASETS:
  for purity in PURITIES:
   for seed in SEEDS:
    code=int(round(purity*100)); eid=f'purv1-{name}-p{code:03d}-s{seed}'; cfg={'experiment_id':eid,'algorithm':'cleanroom-original-gbc-purity-scan','dataset':f'openml-{did}-{name}',
     'dataset_generation_parameters':{'openml_data_id':did,'max_samples':cap,'subsampling':'stratified before split if source exceeds cap'},'pool':'exploration','seed':seed,
     'runner':'experiments.runners.real_gbc_trial:run','hyperparameters':{'purity':purity},'search':{'enabled':True,'campaign':'real_purity_v1','purity':purity}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated',len(DATASETS)*len(PURITIES)*len(SEEDS),'purity configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl'; completed={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}; paths=sorted((ROOT/'experiments/configs/real_validation/purity_v1').glob('*.json'))
 for i,path in enumerate(paths,1):
  cfg=json.loads(path.read_text())
  if cfg['experiment_id'] in completed: continue
  r=run_from_config(path,result); print(i,len(paths),r['experiment_id'],r['outcome'],r['accuracy'],r['granule_count'],flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv: generate()
 if '--generate-only' not in sys.argv: run()
