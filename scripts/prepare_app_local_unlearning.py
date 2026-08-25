"""Freeze fixed-region approximate-unlearning configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("breast_cancer", "wine", "digits", "satimage")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/local_unlearning_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appunlearn-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-local-unlearning",
                "algorithm": "gb-fixed-region-approximate-unlearning",
                "dataset": f"semi-real-unlearning-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 1200},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_local_unlearning:run",
                "hyperparameters": {
                    "deletion_fraction": 0.10,
                    "scenarios": ["random", "local_concentrated", "class_skew"],
                },
                "search": {"enabled": False, "campaign": "app_local_unlearning_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} unlearning configs")


if __name__ == "__main__":
    main()
