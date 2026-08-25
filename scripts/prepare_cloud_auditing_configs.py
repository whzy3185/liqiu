"""Generate the frozen five-seed Cloud Auditing Cheap Test C configs."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "cloud_auditing_v1"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for seed in (1, 7, 21, 42, 2026):
        experiment_id = f"cloud-auditing-v1-s{seed}"
        config = {
            "experiment_id": experiment_id,
            "algorithm": "cloud-auditing-fixed-budget-v1",
            "dataset": "synthetic-cloud-blocks-v1",
            "dataset_generation_parameters": {"sizes": [10000, 100000]},
            "pool": "exploration",
            "seed": seed,
            "runner": "experiments.runners.cloud_auditing:run",
            "hyperparameters": {"repeats": 30},
            "search": {"enabled": False},
        }
        (OUT / f"{experiment_id}.json").write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(f"wrote 5 configs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

