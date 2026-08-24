"""CLI entry point for one configuration-driven experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_core import run_from_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("experiments/results/experiments.jsonl"))
    args = parser.parse_args()
    record = run_from_config(args.config, args.output)
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if record["outcome"] != "failure" else 1


if __name__ == "__main__":
    raise SystemExit(main())

