"""Generate/run Candidate 3 boundary-metric predictive audit."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
SEEDS=(1,7,21,42,2026);COMMIT='5986bea652f7e6e944af33572cc958cd096de5a1';METHODS={'original':('upstream-gbc-original-boundary-metric','work/upstreams/syxiaa_GBC/gb_origin.py'),'adaptive':('upstream-gbc-adaptive-boundary-metric','work/upstreams/syxiaa_GBC/gb_adaptive_upload.py')}
CASES=[('xor05',{'family':'xor','overlap':.05}),('xor25',{'family':'xor','overlap':.25}),('gx25',{'family':'gaussian_xor','overlap':.25}),('gx40',{'family':'gaussian_xor','overlap':.40}),('cb04',{'family':'checkerboard','cells':4,'manifold_width':.05}),('cb06',{'family':'checkerboard','cells':6,'manifold_width':.05}),('sw04',{'family':'sector_wheel','sectors':4,'manifold_width':.05}),('sw08',{'family':'sector_wheel','sectors':8,'manifold_width':.05}),('sw12',{'family':'sector_wheel','sectors':12,'manifold_width':.05})]
def generate():
 out=ROOT/'experiments/configs/candidates/boundary_metric_v1';out.mkdir(parents=True,exist_ok=True)
 for case,params in CASES:
  for variant,(algorithm,path) in METHODS.items():
   for seed in SEEDS:
    eid=f'bmv1-{case}-{variant}-s{seed}';generation={'n_samples':600,'ambient_dimension':2,'label_noise':'none','noise_rate':0,'feature_noise':0,'outlier_rate':0,**params};cfg={'experiment_id':eid,'algorithm':algorithm,'dataset':'boundary-metric-audit-v1','dataset_generation_parameters':generation,'pool':'exploration','seed':seed,'runner':'experiments.runners.failure_trial:run','variant':variant,'upstream_path':path,'upstream_commit':COMMIT,'hyperparameters':{'purity':.85} if variant=='original' else {},'search':{'enabled':False,'campaign':'boundary_metric_v1','case':case}}
    (out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('Generated 90 boundary-metric configs')
def run():
 from research_core import run_from_config
 result=ROOT/'experiments/results/experiments.jsonl';done={json.loads(x)['experiment_id'] for x in result.read_text().splitlines() if x}
 for i,path in enumerate(sorted((ROOT/'experiments/configs/candidates/boundary_metric_v1').glob('*.json')),1):
  c=json.loads(path.read_text())
  if c['experiment_id'] in done:continue
  r=run_from_config(path,result);a=r.get('additional_metrics',{});print(i,90,r['experiment_id'],r['outcome'],a.get('accuracy_gap'),a.get('global_knn_label_mixing'),r['structure'].get('within_ball_knn_mixing'),flush=True)
if __name__=='__main__':
 if '--run-only' not in sys.argv:generate()
 if '--generate-only' not in sys.argv:run()
