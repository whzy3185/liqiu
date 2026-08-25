"""Generate five-seed, three-dataset Secure Aggregation Cheap Test E configs."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "secure_aggregation_v1"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset in ("adult", "breast_cancer", "covertype"):
        for seed in (1, 7, 21, 42, 2026):
            experiment_id = f"secure-aggregation-v1-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "algorithm": "secure-aggregation-compression-v1",
                "dataset": dataset,
                "dataset_generation_parameters": {"name": dataset, "cap": 2000},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.secure_aggregation:run",
                "hyperparameters": {"purity": 0.9},
                "search": {"enabled": False},
            }
            (OUT / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"wrote 15 configs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

