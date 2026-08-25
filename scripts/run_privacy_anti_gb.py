"""Run pending Anti-GB privacy configs."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_core import run_from_config


CONFIGS = ROOT / "experiments" / "configs" / "privacy_anti_gb_v1"
OUTPUT = ROOT / "experiments" / "results" / "experiments.jsonl"


def main() -> int:
    existing = {
        json.loads(line).get("experiment_id")
        for line in OUTPUT.read_text(encoding="utf-8").splitlines()
        if line
    }
    failed = 0
    for path in sorted(CONFIGS.glob("*.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        if config["experiment_id"] in existing:
            continue
        record = run_from_config(path, OUTPUT)
        print(record["experiment_id"], record["outcome"], f"{record['runtime_seconds']:.2f}s")
        failed += record["outcome"] == "failure"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

