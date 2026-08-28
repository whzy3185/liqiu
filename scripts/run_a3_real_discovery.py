"""Checkpointed strict cross-release A3 discovery over the frozen task pool."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from studies.privacy_refinement.a3_real_strict import DISCOVERY_IDS, evaluate_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+", default=list(DISCOVERY_IDS))
    parser.add_argument("--output", type=Path, default=Path("results/A3_real_discovery.csv"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    root = Path("datasets/real/a3_approved")
    for source_dataset_id in args.ids:
        if args.resume and args.output.exists() and source_dataset_id in set(pd.read_csv(args.output).source_dataset_id):
            print({"status": "SKIP_COMPLETE", "source_dataset_id": source_dataset_id})
            continue
        kwargs = {"outer_seeds": (1,), "thresholds": (.90,), "levels": ("release_1",), "shadow_count": 2, "target_count": 1, "max_pool": 400} if args.smoke else {}
        result = evaluate_dataset(source_dataset_id, root, **kwargs)
        result.to_csv(args.output, mode="a", index=False, header=not args.output.exists())
        print({"status": "DONE", "source_dataset_id": source_dataset_id, "rows": len(result)})


if __name__ == "__main__":
    main()
