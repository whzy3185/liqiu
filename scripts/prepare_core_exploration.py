"""Freeze GB-only noise, imbalance and shift stress configurations."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SEEDS=(1,7,21,42,2026);METHODS=('kmeans','class_means')
def write(out,eid,cfg):out.mkdir(parents=True,exist_ok=True);(out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
def main():
 counts={};out=ROOT/'experiments/configs/core_exploration'
 n=0
 for family in ('gaussian_blobs','moons','spirals'):
  for kind in ('symmetric','boundary'):
   for rate in (0,.1,.2,.3):
    for method in METHODS:
     for seed in SEEDS:
      eid=f'gbnoise-{family}-{kind}-r{int(rate*100):02d}-{method}-s{seed}';cfg={'experiment_id':eid,'study':'granular-ball-core-noise','algorithm':f'gb-{method}-noise-frontier','dataset':f'synthetic-{family}-clean-test','dataset_generation_parameters':{'family':family,'noise_kind':kind,'noise_rate':rate,'generation_method':method},'pool':'exploration','seed':seed,'runner':'experiments.runners.core_noise_stress:run','hyperparameters':{'taus':[.60,.75,.85,.95,1.0]},'search':{'enabled':False,'campaign':'gb_core_noise_v1'}};write(out/'noise',eid,cfg);n+=1
 counts['noise']=n;n=0
 for family in ('density_equal','density_shift','moons'):
  for ratio in (1,5,20,50):
   for method in METHODS:
    for seed in SEEDS:
     eid=f'gbimb-{family}-r{ratio:02d}-{method}-s{seed}';cfg={'experiment_id':eid,'study':'granular-ball-core-imbalance','algorithm':f'gb-{method}-imbalance-frontier','dataset':f'synthetic-{family}-balanced-test','dataset_generation_parameters':{'family':family,'imbalance_ratio':ratio,'generation_method':method},'pool':'exploration','seed':seed,'runner':'experiments.runners.core_imbalance_stress:run','hyperparameters':{'taus':[.60,.75,.85,.95,1.0]},'search':{'enabled':False,'campaign':'gb_core_imbalance_v1'}};write(out/'imbalance',eid,cfg);n+=1
 counts['imbalance']=n;n=0
 for shift in ('covariate_shift','concept_drift','prior_shift','density_drift'):
  for method in METHODS:
   for seed in SEEDS:
    eid=f'gbshift-{shift}-{method}-s{seed}';cfg={'experiment_id':eid,'study':'granular-ball-core-shift','algorithm':f'gb-{method}-shift-confidence-frontier','dataset':f'synthetic-stream-{shift}','dataset_generation_parameters':{'shift_kind':shift,'generation_method':method},'pool':'exploration','seed':seed,'runner':'experiments.runners.core_shift_stress:run','hyperparameters':{'taus':[.60,.75,.85,.95,1.0]},'search':{'enabled':False,'campaign':'gb_core_shift_v1'}};write(out/'shift',eid,cfg);n+=1
 counts['shift']=n;print(counts,'total',sum(counts.values()))
if __name__=='__main__':main()
