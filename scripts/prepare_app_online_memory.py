"""Freeze the hard-budget local regranulation kill test."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KINDS = ("concept_drift", "covariate_shift", "emerging_class")
SEEDS = (1, 7, 21)


def main():
    output = ROOT / "experiments/configs/application_exploration/online_memory_v1"
    output.mkdir(parents=True, exist_ok=True)
    for kind in KINDS:
        for seed in SEEDS:
            experiment_id = f"apponline-{kind}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "study": "granular-ball-application-online-memory",
                "algorithm": "gb-hard-budget-local-online-memory",
                "dataset": f"synthetic-stream-{kind}",
                "dataset_generation_parameters": {"stream_kind": kind},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.app_online_memory:run",
                "hyperparameters": {"max_balls": 24, "alpha": 0.35, "expire_steps": 3},
                "search": {"enabled": False, "campaign": "app_online_memory_v1"},
            }
            (output / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"Generated {len(KINDS) * len(SEEDS)} online-memory configs")


if __name__ == "__main__":
    main()
