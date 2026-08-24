import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATASETS=('cora','citeseer','pubmed');SEEDS=(1,7,21);RATIOS=(.25,.5,.75)
def main():
 out=ROOT/'experiments/configs/v2/gnn';out.mkdir(parents=True,exist_ok=True);count=0
 for dataset in DATASETS:
  for seed in SEEDS:
   specs=[('full',1.),('gbgc_adaptive',None)]+[(m,r) for m in ('random','heavy_edge','gbgc_fixed') for r in RATIOS]
   for method,ratio in specs:
    suffix=method if ratio is None else f'{method}-r{int(ratio*100):02d}';eid=f'v2gnn-{dataset}-{suffix}-s{seed}';cfg={'experiment_id':eid,'study':'gnn-risk-granularity-v2','algorithm':f'gnn-{method}-frontier','dataset':f'planetoid-{dataset}','dataset_generation_parameters':{'dataset':dataset},'pool':'exploration','seed':seed,'runner':'experiments.runners.v2_gnn_frontier:run','hyperparameters':{'method':method,'ratio':ratio},'search':{'enabled':False,'campaign':'v2_gnn_frontier_v1'}};(out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n');count+=1
 print('generated',count,'GNN configs')
if __name__=='__main__':main()
