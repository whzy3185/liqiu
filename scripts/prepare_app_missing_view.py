"""Freeze missing-view recovery configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("satimage", "digits", "breast_cancer", "wine")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/missing_view_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appmissing-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-missing-view",
                "algorithm": "gb-cross-view-region-recovery",
                "dataset": f"semi-real-missing-view-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 2400},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_missing_view:run",
                "hyperparameters": {"missing_rates": [0.20, 0.40, 0.60]},
                "search": {"enabled": False, "campaign": "app_missing_view_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} missing-view configs")


if __name__ == "__main__":
    main()
