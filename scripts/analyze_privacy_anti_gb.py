"""Determine whether tuned non-GB summaries eliminate the privacy signal."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "results" / "experiments.jsonl"
CSV = ROOT / "experiments" / "results" / "privacy_anti_gb_v1.csv"
REPORT = ROOT / "reports" / "privacy_anti_gb.md"
ANALYSIS = ROOT / "privacy_security" / "analysis.md"
DECISION = ROOT / "privacy_security" / "decision.md"


def main() -> int:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    records = [record for record in records if record.get("algorithm") == "privacy-anti-gb-v1"]
    rows = []
    for record in records:
        if record["outcome"] != "success":
            continue
        for result in record["additional_metrics"]["rows"]:
            rows.append(
                {
                    "experiment_id": record["experiment_id"],
                    "dataset": record["dataset"],
                    "seed": record["seed"],
                    **{key: value for key, value in result.items() if key != "metrics"},
                    **result["metrics"],
                }
            )
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "purity_threshold", "method"])
    frame.to_csv(CSV, index=False)
    paired = _paired(frame)
    win_fraction = float((paired.privacy_advantage >= 0.03).mean())
    mean_advantage = float(paired.privacy_advantage.mean())
    decision = "GO" if win_fraction >= 0.7 and mean_advantage >= 0.03 else "KILL"
    report = _report(frame, records, paired, decision, win_fraction, mean_advantage)
    REPORT.write_text(report, encoding="utf-8")
    initial = (ROOT / "reports" / "privacy_leakage_cheap_test.md").read_text(encoding="utf-8")
    ANALYSIS.write_text(initial + "\n\n" + report, encoding="utf-8")
    if decision == "KILL":
        DECISION.write_text("# Decision\n\nKILL\n", encoding="utf-8")
    print(json.dumps({
        "records": len(records),
        "rows": len(frame),
        "paired_conditions": len(paired),
        "mean_privacy_advantage": mean_advantage,
        "win_fraction": win_fraction,
        "decision": decision,
    }, indent=2))
    return 0


def _paired(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["dataset", "seed", "purity_threshold"]
    for key, group in frame.groupby(keys):
        gb = group[group.method == "granular_ball"].iloc[0]
        eligible = group[
            (group.method != "granular_ball")
            & (group.utility_accuracy >= gb.utility_accuracy - 0.02)
        ]
        best = eligible.sort_values("membership_roc_auc").iloc[0]
        rows.append({
            **dict(zip(keys, key)),
            "gb_auc": gb.membership_roc_auc,
            "gb_utility": gb.utility_accuracy,
            "best_method": best.method,
            "baseline_auc": best.membership_roc_auc,
            "baseline_utility": best.utility_accuracy,
            "privacy_advantage": best.membership_roc_auc - gb.membership_roc_auc,
        })
    return pd.DataFrame(rows)


def _report(frame, records, paired, decision, win_fraction, mean_advantage) -> str:
    sensitivity = paired.groupby("purity_threshold").privacy_advantage.agg(["mean", "std"]).round(4)
    winners = paired.best_method.value_counts().rename_axis("method").reset_index(name="cells")
    failures = sum(record["outcome"] != "success" for record in records)
    return f"""# Privacy Anti-GB Test

## Design

The test stays on Adult and Bank Marketing, where the original signal was
strongest. For each GB purity and seed, all competitors use the same number of
released regions. A competitor is eligible only if its utility is within 0.02
of GB; the lowest membership AUC among eligible competitors attacks the claim.

## Result

- Matched conditions: {len(paired)}
- Mean privacy advantage (best eligible baseline AUC minus GB AUC): {mean_advantage:.4f}
- Fraction where GB retains at least 0.03 lower AUC: {win_fraction:.3f}
- Failed configurations: {failures}

Best competing method counts:

```text
{winners.to_string(index=False)}
```

Purity sensitivity:

```text
{sensitivity.to_string()}
```

## Interpretation

The anti-GB gate is stricter than the initial KMeans-only comparator. It includes
tuned KMeans, complete/average/ward hierarchy, random matched groups, tree
leaves, farthest-point local prototypes, and a deliberately label-aware oracle
partition. If one of these matches utility with lower leakage, ball geometry is
not necessary for the observed tradeoff.

## Decision

**{decision}**
"""


if __name__ == "__main__":
    raise SystemExit(main())
