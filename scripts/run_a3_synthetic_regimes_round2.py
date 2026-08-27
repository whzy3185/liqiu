"""Frozen second discovery grid for A3 structural conditions."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from studies.privacy_refinement.a3 import run_arrays, synthetic_regime


def append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def existing(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["dataset"], int(row["seed"])) for row in csv.DictReader(handle)}


def main() -> None:
    results = Path("results/A3_synthetic_round2_raw.csv")
    balls = Path("results/A3_synthetic_round2_balls.jsonl")
    manifest = Path("artifacts/A3_synthetic_round2_manifest.jsonl")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    done = existing(results)
    for dimension in (20, 80):
        for redundant_fraction in (0.0, 0.8):
            for label_noise in (0.0, 0.10):
                params = {"n": 600, "dimension": dimension, "separation": 2.0, "density_ratio": 5.0, "minority_fraction": 0.30, "modes": 3, "redundant_fraction": redundant_fraction, "label_noise": label_noise}
                dataset = f"syn2_d{dimension}_redundant{redundant_fraction:g}_noise{label_noise:g}"
                for seed in (42, 99, 2026):
                    if (dataset, seed) in done:
                        print(f"SKIP {(dataset, seed)}", flush=True)
                        continue
                    print(f"START {(dataset, seed)}", flush=True)
                    x, y = synthetic_regime(seed=seed, **params)
                    rows, ball_rows, meta = run_arrays(dataset, x, y, "controlled_gaussian_mixture_round2", seed, context=params)
                    append_csv(results, rows)
                    with balls.open("a", encoding="utf-8") as handle:
                        for row in ball_rows:
                            handle.write(json.dumps(row, default=lambda value: value.item() if hasattr(value, "item") else str(value)) + "\n")
                    with manifest.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(meta) + "\n")
                    print(f"DONE {(dataset, seed)} rows={len(rows)}", flush=True)


if __name__ == "__main__":
    main()
