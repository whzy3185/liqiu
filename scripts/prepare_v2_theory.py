"""Freeze 24 random heterogeneous settings × five required seeds."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('A','B','C','D');SEEDS=(1,7,21,42,2026);Q=(.55,.60,.70,.80);W=(.2,.5,.8);N=(500,1000,5000);D=(2,10,50);NOISE=(0,.05,.10)
def main():
 rng=np.random.default_rng(20260824);out=ROOT/'experiments/configs/v2/theory';out.mkdir(parents=True,exist_ok=True);count=0
 for family in FAMILIES:
  for base in range(6):
   params={'family':family,'q':float(rng.choice(Q)),'mixture_weight':float(rng.choice(W)),'n':int(rng.choice(N)),'dimension':int(rng.choice(D)),'noise':float(rng.choice(NOISE)),'base_config':f'{family}{base:02d}'}
   for seed in SEEDS:
    eid=f'v2thy-{family}{base:02d}-s{seed}';cfg={'experiment_id':eid,'study':'risk-granularity-v2','algorithm':'v2-independent-risk-budget-tree-cut','dataset':f'v2-heterogeneous-family-{family}','dataset_generation_parameters':params,'pool':'exploration','seed':seed,'runner':'experiments.runners.v2_theory_frontier:run','hyperparameters':{'thresholds':[.55,.60,.65,.70,.75,.80,.85,.90,.95,1.0],'epsilons':[0,.005,.01,.02,.05]},'search':{'enabled':False,'campaign':'v2_theory_frontier_v1'}};(out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n');count+=1
 print('generated',count,'theory configs')
if __name__=='__main__':main()
