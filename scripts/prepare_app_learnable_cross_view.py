"""Freeze learnable anisotropic cross-view configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("satimage", "digits", "breast_cancer", "wine")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/learnable_cross_view_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"applearn-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-learnable-cross-view",
                "algorithm": "anisotropic-differentiable-gb-cross-view",
                "dataset": f"semi-real-learnable-view-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 2400},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_learnable_cross_view:run",
                "hyperparameters": {"epochs": 80, "missing_rates": [0.20, 0.40, 0.60]},
                "search": {"enabled": False, "campaign": "app_learnable_cross_view_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} learnable-cross-view configs")


if __name__ == "__main__":
    main()
