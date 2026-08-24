"""Freeze the first GB application test: low-memory distribution monitoring."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHIFTS = ("translation", "local_emergence", "variance", "mixture_weight")
SEEDS = (1, 7, 21, 42, 2026)


def main():
    output = ROOT / "experiments/configs/application_exploration/drift_sketch_v1"
    output.mkdir(parents=True, exist_ok=True)
    for shift in SHIFTS:
        for seed in SEEDS:
            experiment_id = f"appdrift-{shift}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-drift-sketch",
                "algorithm": "gb-fixed-memory-distribution-sketch",
                "dataset": f"synthetic-monitoring-{shift}",
                "dataset_generation_parameters": {
                    "shift_kind": shift,
                    "dimension": 6,
                    "reference_size": 1200,
                    "batch_size": 200,
                },
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_drift_sketch:run",
                "hyperparameters": {
                    "budgets": [8, 16, 32],
                    "severities": [0.2, 0.4, 0.6, 0.8, 1.0],
                    "calibration_batches": 20,
                    "repeats": 10,
                },
                "search": {"enabled": False, "campaign": "app_drift_sketch_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    print(f"Generated {len(SHIFTS) * len(SEEDS)} drift-sketch configs")


if __name__ == "__main__":
    main()
