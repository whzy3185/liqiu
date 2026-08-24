"""Independent-generator replication for alternating local label structure."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SEEDS=(1,7,21,42,2026); COMMIT="5986bea652f7e6e944af33572cc958cd096de5a1"
METHODS={"original":("upstream-gbc-original-alternating-replication","work/upstreams/syxiaa_GBC/gb_origin.py"),
         "adaptive":("upstream-gbc-adaptive-alternating-replication","work/upstreams/syxiaa_GBC/gb_adaptive_upload.py")}
CASES=[
 ("gx10",{"family":"gaussian_xor","overlap":.10}),
 ("gx25",{"family":"gaussian_xor","overlap":.25}),
 ("gx40",{"family":"gaussian_xor","overlap":.40}),
 ("cb02",{"family":"checkerboard","cells":2,"manifold_width":.05}),
 ("cb04",{"family":"checkerboard","cells":4,"manifold_width":.05}),
 ("cb06",{"family":"checkerboard","cells":6,"manifold_width":.05}),
 ("sw04",{"family":"sector_wheel","sectors":4,"manifold_width":.05}),
 ("sw08",{"family":"sector_wheel","sectors":8,"manifold_width":.05}),
 ("sw12",{"family":"sector_wheel","sectors":12,"manifold_width":.05}),
]
def generate():
 out=ROOT/"experiments/configs/failure_search/alternating_v1"; out.mkdir(parents=True,exist_ok=True)
 for case,params in CASES:
  for variant,(algorithm,path) in METHODS.items():
   for seed in SEEDS:
    eid=f"altv1-{case}-{variant}-s{seed}"; generation={"n_samples":600,"ambient_dimension":2,"label_noise":"none","noise_rate":0,"feature_noise":0,"outlier_rate":0,**params}
    cfg={"experiment_id":eid,"algorithm":algorithm,"dataset":"alternating-label-replication-v1","dataset_generation_parameters":generation,
         "pool":"exploration","seed":seed,"runner":"experiments.runners.failure_trial:run","variant":variant,"upstream_path":path,
         "upstream_commit":COMMIT,"hyperparameters":{"purity":.85} if variant=="original" else {},"search":{"enabled":True,"campaign":"alternating_v1","case":case}}
    (out/f"{eid}.json").write_text(json.dumps(cfg,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(f"Generated {len(CASES)*len(METHODS)*len(SEEDS)} alternating-label configs")
def run():
 from research_core import run_from_config
 result=ROOT/"experiments/results/experiments.jsonl"; completed={json.loads(x)["experiment_id"] for x in result.read_text().splitlines() if x}; paths=sorted((ROOT/"experiments/configs/failure_search/alternating_v1").glob('*.json'))
 for i,path in enumerate(paths,1):
  cfg=json.loads(path.read_text())
  if cfg['experiment_id'] in completed: continue
  r=run_from_config(path,result); print(i,len(paths),r['experiment_id'],r['outcome'],r.get('additional_metrics',{}).get('accuracy_gap'),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--generate-only',action='store_true'); p.add_argument('--run-only',action='store_true'); a=p.parse_args()
 if not a.run_only: generate()
 if not a.generate_only: run()
