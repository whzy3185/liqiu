"""Generate the frozen five-seed Multi-Auditor Cheap Test D configs."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "multi_auditor_v1"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for seed in (1, 7, 21, 42, 2026):
        experiment_id = f"multi-auditor-v1-s{seed}"
        config = {
            "experiment_id": experiment_id,
            "algorithm": "multi-auditor-trust-v1",
            "dataset": "synthetic-multi-auditor-v1",
            "dataset_generation_parameters": {
                "auditors": [20, 50, 100],
                "malicious_ratio": [0.1, 0.3],
                "collusion_strength": [0.5, 1.0],
                "drift": [0.0, 0.2],
            },
            "pool": "exploration",
            "seed": seed,
            "runner": "experiments.runners.multi_auditor:run",
            "hyperparameters": {},
            "search": {"enabled": False},
        }
        (OUT / f"{experiment_id}.json").write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(f"wrote 5 configs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

