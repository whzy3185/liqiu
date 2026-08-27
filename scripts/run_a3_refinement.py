"""Checkpointable A3 cheap-test runner."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from studies.privacy_refinement.a3 import run_seed


def append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def completed(result_path: Path, dataset: str) -> set[int]:
    if not result_path.exists():
        return set()
    with result_path.open(newline="", encoding="utf-8") as handle:
        return {int(row["seed"]) for row in csv.DictReader(handle) if row["dataset"] == dataset}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 7, 21, 42, 2026])
    parser.add_argument("--cache", type=Path, default=Path("datasets/real/a3_openml"))
    parser.add_argument("--results", type=Path, default=Path("results/A3_raw.csv"))
    parser.add_argument("--balls", type=Path, default=Path("results/A3_balls.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/A3_dataset_manifest.jsonl"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    args.cache.mkdir(parents=True, exist_ok=True)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.balls.parent.mkdir(parents=True, exist_ok=True)
    for dataset in args.datasets:
        done = completed(args.results, dataset) if args.resume else set()
        for seed in args.seeds:
            if seed in done:
                print(f"SKIP dataset={dataset} seed={seed}", flush=True)
                continue
            print(f"START dataset={dataset} seed={seed}", flush=True)
            rows, balls, manifest = run_seed(dataset, seed, args.cache)
            append_csv(args.results, rows)
            with args.balls.open("a", encoding="utf-8") as handle:
                for ball in balls:
                    handle.write(json.dumps(ball, default=lambda value: value.item() if hasattr(value, "item") else str(value)) + "\n")
            with args.manifest.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(manifest) + "\n")
            print(f"DONE dataset={dataset} seed={seed} rows={len(rows)} balls={len(balls)}", flush=True)


if __name__ == "__main__":
    main()
