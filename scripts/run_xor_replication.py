"""Generate/run PH-001 XOR dimension and overlap replication campaign."""

import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SEEDS=(1,7,21,42,2026); DIMS=(2,5,10,20,50,100,500); OVERLAPS=(.05,.25)
METHODS={"original":("upstream-gbc-original-xor-replication","work/upstreams/syxiaa_GBC/gb_origin.py"),
         "adaptive":("upstream-gbc-adaptive-xor-replication","work/upstreams/syxiaa_GBC/gb_adaptive_upload.py")}
COMMIT="5986bea652f7e6e944af33572cc958cd096de5a1"

def generate():
    out=ROOT/"experiments/configs/failure_search/xor_v1"; out.mkdir(parents=True,exist_ok=True)
    for dim in DIMS:
      for overlap in OVERLAPS:
       for variant,(algorithm,path) in METHODS.items():
        for seed in SEEDS:
         ov=int(overlap*100); eid=f"xorv1-d{dim:03d}-o{ov:02d}-{variant}-s{seed}"
         cfg={"experiment_id":eid,"algorithm":algorithm,"dataset":"xor-targeted-replication-v1",
              "dataset_generation_parameters":{"family":"xor","n_samples":500,"ambient_dimension":dim,
                 "overlap":overlap,"label_noise":"none","noise_rate":0,"feature_noise":0,"outlier_rate":0},
              "pool":"exploration","seed":seed,"runner":"experiments.runners.failure_trial:run","variant":variant,
              "upstream_path":path,"upstream_commit":COMMIT,"hyperparameters":{"purity":.85} if variant=="original" else {},
              "search":{"enabled":True,"campaign":"xor_v1","dimension":dim,"overlap":overlap}}
         (out/f"{eid}.json").write_text(json.dumps(cfg,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"Generated {len(DIMS)*len(OVERLAPS)*len(METHODS)*len(SEEDS)} XOR configs")

def run():
    from research_core import run_from_config
    result_path=ROOT/"experiments/results/experiments.jsonl"; completed={json.loads(x)["experiment_id"] for x in result_path.read_text().splitlines() if x}
    paths=sorted((ROOT/"experiments/configs/failure_search/xor_v1").glob("*.json"))
    for i,path in enumerate(paths,1):
        cfg=json.loads(path.read_text())
        if cfg["experiment_id"] in completed: continue
        r=run_from_config(path,result_path); print(i,len(paths),r["experiment_id"],r["outcome"],r.get("additional_metrics",{}).get("accuracy_gap"),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--generate-only",action="store_true"); p.add_argument("--run-only",action="store_true"); a=p.parse_args()
    if not a.run_only: generate()
    if not a.generate_only: run()
