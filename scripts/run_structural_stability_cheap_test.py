"""Run the frozen structural-stability v1 cheap test with dataset checkpoints."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from studies.structural_stability.cheap_test import DATASETS, evaluate_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=list(DATASETS))
    parser.add_argument("--output", type=Path, default=Path("results/structural_stability_cheap_test.csv"))
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    completed = set()
    if args.resume and args.output.exists():
        completed = set(pd.read_csv(args.output).dataset)
    root = Path("datasets/real/a3_approved")
    for dataset in args.datasets:
        if dataset in completed:
            print({"status": "SKIP_COMPLETE", "dataset": dataset})
            continue
        frame = pd.DataFrame(evaluate_dataset(dataset, root, smoke=args.smoke))
        frame.to_csv(args.output, mode="a", index=False, header=not args.output.exists())
        print({"status": "DONE", "dataset": dataset, "rows": len(frame)})


if __name__ == "__main__":
    main()
