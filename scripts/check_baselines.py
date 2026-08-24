"""Verify the minimum runnable core-baseline gate and its experiment evidence."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    registry = list(csv.DictReader((ROOT / "baselines/upstream_registry.csv").open(encoding="utf-8")))
    records = [json.loads(line) for line in (ROOT / "experiments/results/experiments.jsonl").read_text(encoding="utf-8").splitlines() if line]
    successful = {r["algorithm"] for r in records if r["outcome"] == "success"}
    expected = {"upstream-gbc-original-generation", "upstream-gbc-adaptive-generation",
                "upstream-gbrs-feature-reduction", "upstream-gbfrs-feature-ranking", "upstream-s3wd-gbrs"}
    assert expected <= successful, f"missing runnable evidence: {sorted(expected-successful)}"
    assert sum("passed" in r["reproduction_status"] for r in registry) >= 5
    assert any(r["algorithm"] == "upstream-gbfrs-feature-ranking" and r["outcome"] == "failure" for r in records), "negative result was lost"
    print(f"Baseline gate passed: {len(expected)} core author-code paths runnable; paper-level reproduction remains pending.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
