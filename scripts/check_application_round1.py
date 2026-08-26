"""Verify the first application scout stopped without retaining an unsupported direction."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        "reports/application_scout/application_literature_ranking.md",
        "reports/application_scout/fault_dataset_inventory.md",
        "reports/application_scout/finance_dataset_inventory.md",
        "reports/application_scout/intrusion_dataset_inventory.md",
        "reports/application_scout/raw_baselines.md",
        "reports/application_scout/fault_gbfeat_decision.md",
        "reports/application_scout/finance_decision.md",
        "reports/application_scout/intrusion_decision.md",
        "reports/application_scout/application_round1_ranking.md",
    ]
    assert all((ROOT / path).exists() for path in required)
    ranking = pd.read_csv(ROOT / "results/application_scout/application_round1_ranking.csv")
    assert len(ranking) == 3
    assert set(ranking.decision) == {"KILL"}
    report = (ROOT / "reports/application_scout/application_round1_ranking.md").read_text(encoding="utf-8")
    assert "KEEP 1 | **None**" in report
    assert "**KILL**" in report
    print("Application round 1 verified: no unsupported KEEP/BACKUP retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

