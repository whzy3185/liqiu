"""Generate and execute the bounded random-search campaign v1."""

import argparse, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SEEDS=(1,7,21)
METHODS={
 "original":("upstream-gbc-original-failure-trial","work/upstreams/syxiaa_GBC/gb_origin.py"),
 "adaptive":("upstream-gbc-adaptive-failure-trial","work/upstreams/syxiaa_GBC/gb_adaptive_upload.py"),
}
COMMIT="5986bea652f7e6e944af33572cc958cd096de5a1"

def generate_configs(trials=12):
    rng=np.random.default_rng(20260824); out=ROOT/"experiments/configs/failure_search/campaign_v1"; out.mkdir(parents=True,exist_ok=True)
    families=("gaussian_blobs","moons","circles","xor","checkerboard","spirals","thin_manifold","nested_clusters","anisotropic","multimodal_class","varying_density","imbalanced_density")
    for trial in range(trials):
        family=families[trial%len(families)]
        label_noise=str(rng.choice(["none","symmetric","boundary","asymmetric"])); noise_rate=0.0 if label_noise=="none" else float(rng.choice([.05,.1,.2]))
        params={"family":family,"n_samples":400,"ambient_dimension":int(rng.choice([2,2,2,5,20,100])),
                "separation":float(rng.uniform(.5,3.0)),"overlap":float(rng.uniform(.03,.5)),
                "curvature":float(rng.uniform(1,4)),"density_ratio":float(np.exp(rng.uniform(0,np.log(20)))),
                "imbalance_ratio":float(np.exp(rng.uniform(0,np.log(20)))),"manifold_width":float(rng.uniform(.02,.3)),
                "label_noise":label_noise,"noise_rate":noise_rate,"feature_noise":float(rng.choice([0,.02,.05,.1])),
                "outlier_rate":float(rng.choice([0,0,.02,.05,.1]))}
        for variant,(algorithm,path) in METHODS.items():
            for seed in SEEDS:
                eid=f"fsv1-t{trial:03d}-{variant}-s{seed}"
                config={"experiment_id":eid,"algorithm":algorithm,"dataset":f"failure-search-{family}-v1",
                        "dataset_generation_parameters":params,"pool":"exploration","seed":seed,
                        "runner":"experiments.runners.failure_trial:run","variant":variant,"upstream_path":path,
                        "upstream_commit":COMMIT,"hyperparameters":{"purity":.85} if variant=="original" else {},
                        "search":{"enabled":True,"campaign":"v1","trial":trial}}
                (out/f"{eid}.json").write_text(json.dumps(config,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"Generated {trials*len(METHODS)*len(SEEDS)} configs in {out}")

def run_configs():
    from research_core import run_from_config
    out=ROOT/"experiments/results/experiments.jsonl"; paths=sorted((ROOT/"experiments/configs/failure_search/campaign_v1").glob("*.json"))
    completed={json.loads(line)["experiment_id"] for line in out.read_text(encoding="utf-8").splitlines() if line}
    for i,path in enumerate(paths,1):
        config=json.loads(path.read_text());
        if config["experiment_id"] in completed: continue
        record=run_from_config(path,out); print(i,len(paths),record["experiment_id"],record["outcome"],record.get("additional_metrics",{}).get("failure_score"),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--generate-only",action="store_true"); p.add_argument("--run-only",action="store_true"); a=p.parse_args()
    if not a.run_only: generate_configs()
    if not a.generate_only: run_configs()
