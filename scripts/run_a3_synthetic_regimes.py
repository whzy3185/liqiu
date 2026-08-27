"""Checkpointable synthetic discovery grid for A3 conditional-regime search."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from studies.privacy_refinement.a3 import run_arrays, synthetic_regime


def append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def complete(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["dataset"], int(row["seed"])) for row in csv.DictReader(handle)}


def configurations() -> list[dict[str, object]]:
    out = []
    for separation in (0.75, 2.0):
        for density_ratio in (1.0, 5.0):
            for minority_fraction in (0.10, 0.30):
                for modes in (1, 3):
                    params = {"n": 600, "dimension": 20, "separation": separation, "density_ratio": density_ratio, "minority_fraction": minority_fraction, "modes": modes, "redundant_fraction": 0.50, "label_noise": 0.02}
                    params["dataset"] = f"syn_sep{separation:g}_density{density_ratio:g}_minority{minority_fraction:g}_modes{modes}"
                    out.append(params)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 7, 21])
    parser.add_argument("--results", type=Path, default=Path("results/A3_synthetic_raw.csv"))
    parser.add_argument("--balls", type=Path, default=Path("results/A3_synthetic_balls.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/A3_synthetic_manifest.jsonl"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    args.results.parent.mkdir(parents=True, exist_ok=True)
    done = complete(args.results) if args.resume else set()
    for params in configurations():
        for seed in args.seeds:
            key = (str(params["dataset"]), seed)
            if key in done:
                print(f"SKIP {key}", flush=True)
                continue
            print(f"START {key}", flush=True)
            x, y = synthetic_regime(seed=seed, **{key: value for key, value in params.items() if key != "dataset"})
            rows, balls, manifest = run_arrays(str(params["dataset"]), x, y, "controlled_gaussian_mixture", seed, context={key: value for key, value in params.items() if key != "dataset"})
            append_csv(args.results, rows)
            with args.balls.open("a", encoding="utf-8") as handle:
                for ball in balls:
                    handle.write(json.dumps(ball, default=lambda value: value.item() if hasattr(value, "item") else str(value)) + "\n")
            with args.manifest.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(manifest) + "\n")
            print(f"DONE {key} rows={len(rows)}", flush=True)


if __name__ == "__main__":
    main()
