"""Generate frozen Anti-GB privacy configs without expanding datasets."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "privacy_anti_gb_v1"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset in ("adult", "bank_marketing"):
        for seed in (1, 7, 21, 42, 2026):
            revision = "v1b" if dataset == "bank_marketing" else "v1"
            experiment_id = f"privacy-anti-gb-{revision}-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "algorithm": "privacy-anti-gb-v1",
                "dataset": dataset,
                "dataset_generation_parameters": {"name": dataset, "cap": 2000},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.privacy_anti_gb:run",
                "hyperparameters": {"purity_scan": [0.8, 0.9, 0.95]},
                "search": {"enabled": False},
            }
            (OUT / f"{experiment_id}.json").write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(f"wrote 10 configs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
