"""Freeze k-anonymous granular-ball microaggregation configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("breast_cancer", "wine", "digits", "covertype")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/privacy_microaggregation_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            experiment_id = f"appprivacy-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-privacy-microaggregation",
                "algorithm": "gb-k-anonymous-microaggregation",
                "dataset": f"semi-real-private-table-{dataset}",
                "dataset_generation_parameters": {"dataset": dataset, "max_samples": 1000},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_privacy_microaggregation:run",
                "hyperparameters": {"k_values": [5, 10, 20]},
                "search": {"enabled": False, "campaign": "app_privacy_microaggregation_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(DATASETS) * len(SEEDS)} privacy configs")


if __name__ == "__main__":
    main()
