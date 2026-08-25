"""Apply the frozen Multi-Auditor GB-specific gate."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "results" / "experiments.jsonl"
CSV = ROOT / "experiments" / "results" / "multi_auditor_v1.csv"
DIRECTION_CSV = ROOT / "multi_auditor" / "results.csv"
REPORT = ROOT / "reports" / "multi_auditor_cheap_test.md"
ANALYSIS = ROOT / "multi_auditor" / "analysis.md"
DECISION = ROOT / "multi_auditor" / "decision.md"
GB_METHODS = {"granular_ball", "gb_three_way"}
NON_GB = {"weighted_majority", "beta_reputation", "dawid_skene", "kmeans_trust", "tree_partition", "knn_competence"}


def main() -> int:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    records = [record for record in records if record.get("algorithm") == "multi-auditor-trust-v1"]
    rows = []
    for record in records:
        if record["outcome"] != "success":
            continue
        for result in record["additional_metrics"]["rows"]:
            rows.append(
                {
                    "experiment_id": record["experiment_id"],
                    "seed": record["seed"],
                    **{key: value for key, value in result.items() if key != "metrics"},
                    **result["metrics"],
                }
            )
    frame = pd.DataFrame(rows).sort_values(
        ["n_auditors", "malicious_ratio", "collusion_strength", "drift", "seed", "method"]
    )
    frame.to_csv(CSV, index=False)
    frame.to_csv(DIRECTION_CSV, index=False)
    decision, evidence = _decide(frame)
    report = _report(frame, records, decision, evidence)
    REPORT.write_text(report, encoding="utf-8")
    ANALYSIS.write_text(report, encoding="utf-8")
    DECISION.write_text(f"# Decision\n\n{decision}\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "rows": len(frame), "decision": decision, **evidence}, indent=2))
    return 0


def _decide(frame: pd.DataFrame) -> tuple[str, dict]:
    keys = ["n_auditors", "malicious_ratio", "collusion_strength", "drift", "seed"]
    gb = (
        frame[frame.method.isin(GB_METHODS)]
        .groupby(keys, as_index=False)
        .final_audit_accuracy.max()
        .rename(columns={"final_audit_accuracy": "gb_accuracy"})
    )
    baseline = (
        frame[frame.method.isin(NON_GB)]
        .groupby(keys, as_index=False)
        .final_audit_accuracy.max()
        .rename(columns={"final_audit_accuracy": "baseline_accuracy"})
    )
    paired = gb.merge(baseline, on=keys)
    paired["gain"] = paired.gb_accuracy - paired.baseline_accuracy
    evidence = {
        "paired_conditions": int(len(paired)),
        "mean_accuracy_gain": float(paired.gain.mean()),
        "win_fraction": float((paired.gain >= 0.01).mean()),
        "nonloss_fraction": float((paired.gain >= 0).mean()),
    }
    if evidence["mean_accuracy_gain"] >= 0.01 and evidence["win_fraction"] >= 0.7:
        return "GO", evidence
    if evidence["mean_accuracy_gain"] <= 0 or evidence["win_fraction"] < 0.4:
        return "KILL", evidence
    return "HOLD", evidence


def _report(frame: pd.DataFrame, records: list[dict], decision: str, evidence: dict) -> str:
    failures = [record for record in records if record["outcome"] != "success"]
    summary = (
        frame.groupby("method")[[
            "final_audit_accuracy", "malicious_auroc", "false_trust_rate",
            "additional_audit_cost", "decision_delay",
        ]]
        .mean()
        .round(4)
        .reset_index()
    )
    return f"""# Multi-Auditor Cheap Test D

## Scope

Auditor populations of 20, 50, and 100 are tested under noisy, lazy,
malicious, colluding, adaptive, and drifting behavior. Every method receives the
same history and current response matrix.

## Mean results

```text
{summary.to_string(index=False)}
```

## GB-specific gate

- Matched conditions: {evidence['paired_conditions']}
- Mean GB accuracy gain over the strongest non-GB method: {evidence['mean_accuracy_gain']:.4f}
- Fraction with at least +0.01 gain: {evidence['win_fraction']:.3f}
- Non-loss fraction: {evidence['nonloss_fraction']:.3f}

The strongest comparator is selected per condition from weighted majority,
Beta reputation, Dawid-Skene, matched KMeans, kNN competence, and matched tree
partitions. Failed configurations: {len(failures)}.

## Decision

**{decision}**
"""


if __name__ == "__main__":
    raise SystemExit(main())

