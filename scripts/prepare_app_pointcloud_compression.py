"""Freeze point-cloud compression/retrieval configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGIMES = ("uniform", "density_bias", "outliers", "occlusion")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/pointcloud_compression_v1"
    output.mkdir(parents=True, exist_ok=True)
    for regime in REGIMES:
        for seed in SEEDS:
            experiment_id = f"apppoint-{regime}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-pointcloud-compression",
                "algorithm": "gb-weighted-pointcloud-compression-retrieval",
                "dataset": f"synthetic-shape-gallery-{regime}",
                "dataset_generation_parameters": {"regime": regime, "points": 256},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_pointcloud_compression:run",
                "hyperparameters": {"point_budgets": [32, 64, 128]},
                "search": {"enabled": False, "campaign": "app_pointcloud_compression_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(REGIMES) * len(SEEDS)} point-cloud configs")


if __name__ == "__main__":
    main()
