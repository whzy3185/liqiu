"""Freeze the first contextual cell-cleaning kill test."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("breast_cancer", "wine", "diabetes")
SEEDS = (1, 7, 21, 42, 2026)


def main():
    output = ROOT / "experiments/configs/application_exploration/cell_cleaning_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appclean-{dataset}-contextual-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-cell-cleaning",
                "algorithm": "gb-crossfit-contextual-cell-cleaning",
                "dataset": f"sklearn-{dataset}-contextual-cell-errors",
                "dataset_generation_parameters": {
                    "dataset": dataset,
                    "corruption": "contextual_systematic",
                },
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_cell_cleaning:run",
                "hyperparameters": {"corruption_rate": 0.03, "crossfit_folds": 5},
                "search": {"enabled": False, "campaign": "app_cell_cleaning_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} cell-cleaning configs")


if __name__ == "__main__":
    main()
