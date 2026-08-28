"""Run the frozen strain-disjoint MicroMass A3 Discovery extension."""

from __future__ import annotations

import argparse
from pathlib import Path

from studies.privacy_refinement.a3_group_real_strict import evaluate_micromass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/A3_micromass_group_discovery.csv"))
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    kwargs = {"outer_seeds": (1,), "thresholds": (.90,), "shadow_count": 2, "target_count": 1} if args.smoke else {}
    result = evaluate_micromass(Path("datasets/real/a3_approved"), **kwargs)
    result.to_csv(args.output, index=False)
    print({"status": "DONE", "rows": len(result), "output": str(args.output)})


if __name__ == "__main__":
    main()
