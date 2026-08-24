"""Freeze the matched batch active-learning kill test."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("iris", "wine", "breast_cancer", "digits", "moons")
SEEDS = (1, 7, 21, 42, 2026)


def main():
    output = ROOT / "experiments/configs/application_exploration/active_learning_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appactive-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-active-learning",
                "algorithm": "gb-radius-aware-batch-active-learning",
                "dataset": f"sklearn-{dataset}-active-learning",
                "dataset_generation_parameters": {"dataset": dataset},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_active_learning:run",
                "hyperparameters": {"initial_per_class": 2, "fractions": [0.02, 0.05, 0.10, 0.20]},
                "search": {"enabled": False, "campaign": "app_active_learning_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} active-learning configs")


if __name__ == "__main__":
    main()
