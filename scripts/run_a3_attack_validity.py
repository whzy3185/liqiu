"""Run checkpointed strict A3 cross-release attack-validity regimes."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from studies.privacy_refinement.a3_strict import CONFIRMATION_POINTS, run_validity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--point-index", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/A3_attack_validity.csv"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.point_index < len(CONFIRMATION_POINTS):
        raise ValueError("point-index outside frozen confirmation grid")
    point = CONFIRMATION_POINTS[args.point_index]
    expected = 864
    if args.resume and args.output.exists():
        previous = pd.read_csv(args.output)
        match = previous[
            (previous.dimension == point["dimension"])
            & (previous.redundant_fraction == point["redundant_fraction"])
            & (previous.label_noise == point["label_noise"])
        ]
        if len(match) == expected:
            print({"status": "SKIP_COMPLETE", "point_index": args.point_index, "rows": len(match)})
            return
        if len(match):
            raise RuntimeError("partial strict-gate checkpoint detected; preserve it and inspect before rerun")
    result = run_validity(points=(point,))
    header = not args.output.exists()
    result.to_csv(args.output, mode="a", index=False, header=header)
    print({"status": "DONE", "point_index": args.point_index, "rows": len(result)})


if __name__ == "__main__":
    main()
