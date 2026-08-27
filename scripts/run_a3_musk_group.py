"""Run the frozen group-aware Musk1 A3 experiment."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from studies.privacy_refinement.a3 import load_grouped_dataset, run_arrays


def append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def finished(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["dataset"], int(row["seed"])) for row in csv.DictReader(handle)}


def main() -> None:
    results = Path("results/A3_musk_group_raw.csv")
    balls = Path("results/A3_musk_group_balls.jsonl")
    manifest = Path("artifacts/A3_musk_group_manifest.jsonl")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    x, y, groups, source = load_grouped_dataset("musk1")
    done = finished(results)
    for noise in (0.0, 0.05, 0.10):
        dataset = f"musk1_group_trainnoise{noise:g}"
        for seed in (2, 13, 73, 314, 808):
            if (dataset, seed) in done:
                print(f"SKIP {(dataset, seed)}", flush=True)
                continue
            print(f"START {(dataset, seed)}", flush=True)
            rows, ball_rows, meta = run_arrays(dataset, x, y, source, seed, context={"base_dataset": "musk1", "training_label_noise": noise, "split_protocol": "StratifiedGroupKFold_by_molecule"}, training_label_noise=noise, groups=groups)
            append_csv(results, rows)
            with balls.open("a", encoding="utf-8") as handle:
                for row in ball_rows:
                    handle.write(json.dumps(row, default=lambda value: value.item() if hasattr(value, "item") else str(value)) + "\n")
            with manifest.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(meta) + "\n")
            print(f"DONE {(dataset, seed)} rows={len(rows)}", flush=True)


if __name__ == "__main__":
    main()
