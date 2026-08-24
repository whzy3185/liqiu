"""Freeze local annotator competence and attribution configurations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("moons", "breast_cancer", "digits")
REGIMES = ("axis", "voronoi", "nonlinear", "global_control")
SEEDS = (1, 7, 21, 42, 2026)


def main():
    output = ROOT / "experiments/configs/application_exploration/crowd_competence_v1"
    output.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for regime in REGIMES:
            for seed in SEEDS:
                experiment_id = f"appcrowd-{dataset}-{regime}-s{seed}"
                config = {
                    "experiment_id": experiment_id,
                    "study": "granular-ball-application-crowd-competence",
                    "algorithm": "gb-local-annotator-competence",
                    "dataset": f"semi-real-{dataset}-crowd-{regime}",
                    "dataset_generation_parameters": {"dataset": dataset, "regime": regime},
                    "pool": "exploration",
                    "seed": seed,
                    "runner": "experiments.runners.app_crowd_competence:run",
                    "hyperparameters": {
                        "workers": 16,
                        "competence_labels_per_item": 5,
                        "pool_initial_labels_per_item": 2,
                        "allocation_cost_fractions": [0, 0.25, 0.5, 1.0],
                    },
                    "search": {"enabled": False, "campaign": "app_crowd_competence_v1"},
                }
                (output / f"{experiment_id}.json").write_text(
                    json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
    print(f"Generated {len(DATASETS) * len(REGIMES) * len(SEEDS)} crowd configs")


if __name__ == "__main__":
    main()
