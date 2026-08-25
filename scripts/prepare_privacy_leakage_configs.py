"""Generate the frozen 5-seed Privacy Leakage Cheap Test A configs."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "privacy_leakage_v1"
SEEDS = (1, 7, 21, 42, 2026)
DATASETS = ("adult", "bank_marketing", "german_credit", "breast_cancer", "covertype")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in SEEDS:
            revision = "v1b" if dataset == "bank_marketing" else "v1"
            experiment_id = f"privacy-leakage-{revision}-{dataset}-s{seed}"
            config = {
                "experiment_id": experiment_id,
                "algorithm": "privacy-leakage-summary-attack-v1",
                "dataset": dataset,
                "dataset_generation_parameters": {"name": dataset, "cap": 2000},
                "pool": "exploration",
                "seed": seed,
                "runner": "experiments.runners.privacy_leakage:run",
                "hyperparameters": {"purity": 0.9},
                "search": {"enabled": False},
            }
            path = OUT / f"{experiment_id}.json"
            path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(DATASETS) * len(SEEDS)} configs to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
