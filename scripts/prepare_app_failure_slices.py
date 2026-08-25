"""Freeze model failure-slice discovery configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("moons", "breast_cancer", "digits", "satimage")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/failure_slices_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appslice-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-failure-slices",
                "algorithm": "gb-model-risk-slice-discovery",
                "dataset": f"semi-real-model-audit-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 1200},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_failure_slices:run",
                "hyperparameters": {"target_coverage": 0.20, "localized_corruption": True},
                "search": {"enabled": False, "campaign": "app_failure_slices_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} failure-slice configs")


if __name__ == "__main__":
    main()
