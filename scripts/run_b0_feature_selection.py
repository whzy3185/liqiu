"""Checkpointable B0 shadow-release membership experiment."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from studies.privacy_refinement.b0 import run_seed


def append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def complete(path: Path, dataset: str) -> set[int]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {int(row["seed"]) for row in csv.DictReader(handle) if row["dataset"] == dataset}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-dir", type=Path, required=True)
    parser.add_argument("--datasets", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 7, 21, 42, 2026])
    parser.add_argument("--results", type=Path, default=Path("results/B0_raw.csv"))
    parser.add_argument("--shadows", type=Path, default=Path("results/B0_shadow_outputs.jsonl"))
    parser.add_argument("--shadow-runs", type=int, default=24)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.shadows.parent.mkdir(parents=True, exist_ok=True)
    for dataset in args.datasets:
        done = complete(args.results, dataset) if args.resume else set()
        for seed in args.seeds:
            if seed in done:
                print(f"SKIP dataset={dataset} seed={seed}", flush=True)
                continue
            print(f"START dataset={dataset} seed={seed}", flush=True)
            rows, shadows = run_seed(dataset, seed, args.upstream_dir, shadows=args.shadow_runs)
            append_csv(args.results, rows)
            with args.shadows.open("a", encoding="utf-8") as handle:
                for shadow in shadows:
                    handle.write(json.dumps(shadow) + "\n")
            print(f"DONE dataset={dataset} seed={seed} rows={len(rows)} shadows={len(shadows)}", flush=True)


if __name__ == "__main__":
    main()
