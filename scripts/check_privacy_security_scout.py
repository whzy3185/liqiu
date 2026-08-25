"""Verify that the privacy/security scout is complete and internally consistent."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = {
    "privacy-leakage-summary-attack-v1": (25, 5),
    "cloud-auditing-fixed-budget-v1": (5, 0),
    "multi-auditor-trust-v1": (5, 0),
    "secure-aggregation-compression-v1": (15, 0),
    "privacy-anti-gb-v1": (10, 5),
}


def main() -> int:
    records = [
        json.loads(line)
        for line in (ROOT / "experiments/results/experiments.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    for algorithm, (successes, failures) in ALGORITHMS.items():
        selected = [record for record in records if record.get("algorithm") == algorithm]
        assert sum(record["outcome"] == "success" for record in selected) == successes, algorithm
        assert sum(record["outcome"] == "failure" for record in selected) == failures, algorithm
    assert (ROOT / "privacy_security/decision.md").read_text().strip().endswith("KILL")
    assert (ROOT / "cloud_auditing/decision.md").read_text().strip().endswith("KILL")
    assert (ROOT / "multi_auditor/decision.md").read_text().strip().endswith("KILL")
    assert (ROOT / "secure_aggregation/decision.md").read_text().strip().endswith("KILL")
    assert (ROOT / "dp_granular_ball/decision.md").read_text().splitlines()[2] == "KILL"
    ranking = pd.read_csv(ROOT / "experiments/results/privacy_security_ranking.csv")
    assert len(ranking) == 5 and set(ranking.decision) == {"KILL"}
    assert "ABANDON GB PRIVACY/AUDIT LINE" in (ROOT / "reports/final_research_scout.md").read_text()
    print("Privacy/security scout verified: 60 successes, 10 retained failures, all gates closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

