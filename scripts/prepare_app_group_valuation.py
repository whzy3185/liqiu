"""Freeze granular-ball grouped data-valuation configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("breast_cancer", "wine", "digits", "moons")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/group_valuation_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appvalue-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-group-valuation",
                "algorithm": "gb-grouped-leaveout-data-valuation",
                "dataset": f"semi-real-data-valuation-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 320},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_group_valuation:run",
                "hyperparameters": {"label_noise": 0.10, "max_groups": 40},
                "search": {"enabled": False, "campaign": "app_group_valuation_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} group-valuation configs")


if __name__ == "__main__":
    main()
