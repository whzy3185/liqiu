"""Flatten Cloud Auditing records and apply the frozen GB-specific gate."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "results" / "experiments.jsonl"
CSV = ROOT / "experiments" / "results" / "cloud_auditing_v1.csv"
DIRECTION_CSV = ROOT / "cloud_auditing" / "results.csv"
REPORT = ROOT / "reports" / "cloud_auditing_cheap_test.md"
ANALYSIS = ROOT / "cloud_auditing" / "analysis.md"
DECISION = ROOT / "cloud_auditing" / "decision.md"
GB_METHODS = {"granular_ball", "gb_three_way"}
NON_GB = {"weighted_random", "risk_score", "anomaly_score", "kmeans_group", "tree_partition"}
STRUCTURED = {"clustered", "hot_targeted", "cold_targeted"}


def main() -> int:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    records = [record for record in records if record.get("algorithm") == "cloud-auditing-fixed-budget-v1"]
    rows = []
    for record in records:
        if record["outcome"] != "success":
            continue
        for result in record["additional_metrics"]["rows"]:
            row = {
                "experiment_id": record["experiment_id"],
                "seed": record["seed"],
                **{key: value for key, value in result.items() if key != "metrics"},
                **result["metrics"],
            }
            rows.append(row)
    frame = pd.DataFrame(rows).sort_values(["n_blocks", "scenario", "seed", "budget", "method"])
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
    keys = ["n_blocks", "scenario", "seed", "budget"]
    gb = (
        frame[frame.method.isin(GB_METHODS)]
        .groupby(keys, as_index=False)
        .detection_probability.max()
        .rename(columns={"detection_probability": "gb_detection"})
    )
    baseline = (
        frame[frame.method.isin(NON_GB)]
        .groupby(keys, as_index=False)
        .detection_probability.max()
        .rename(columns={"detection_probability": "baseline_detection"})
    )
    paired = gb.merge(baseline, on=keys)
    paired["gain"] = paired.gb_detection - paired.baseline_detection
    structured = paired[paired.scenario.isin(STRUCTURED)]
    evidence = {
        "paired_cells": int(len(paired)),
        "structured_cells": int(len(structured)),
        "mean_structured_detection_gain": float(structured.gain.mean()),
        "structured_win_fraction": float((structured.gain >= 0.03).mean()),
        "structured_nonloss_fraction": float((structured.gain >= 0).mean()),
        "mean_adversarial_gain": float(paired[paired.scenario == "adversarial"].gain.mean()),
    }
    if evidence["structured_win_fraction"] >= 0.7 and evidence["mean_structured_detection_gain"] >= 0.03:
        return "GO", evidence
    if evidence["mean_structured_detection_gain"] <= 0.01 and evidence["structured_win_fraction"] < 0.4:
        return "KILL", evidence
    return "HOLD", evidence


def _report(frame: pd.DataFrame, records: list[dict], decision: str, evidence: dict) -> str:
    failures = [record for record in records if record["outcome"] != "success"]
    summary = (
        frame.groupby(["scenario", "method"])[
            ["detection_probability", "corruption_recall", "time_to_first_detection", "worst_case_miss_rate"]
        ]
        .mean()
        .round(4)
        .reset_index()
    )
    summary_text = summary.to_string(index=False)
    return f"""# Cloud Auditing Cheap Test C

## Scope

Synthetic clouds contain 10,000 and 100,000 blocks. Every method is evaluated
at the same audited-block budget. The cryptographic PDP/PoR proof is intentionally
out of scope; this test asks only whether risk grouping improves sampling.

## Mean results

```text
{summary_text}
```

## GB-specific gate

- Paired budget/scenario/seed/size cells: {evidence['paired_cells']}
- Structured-corruption cells: {evidence['structured_cells']}
- Mean structured detection gain over the strongest non-GB baseline: {evidence['mean_structured_detection_gain']:.4f}
- Structured cells with at least +0.03 detection gain: {evidence['structured_win_fraction']:.3f}
- Structured non-loss fraction: {evidence['structured_nonloss_fraction']:.3f}
- Mean policy-aware adversarial gain: {evidence['mean_adversarial_gain']:.4f}

The strongest baseline is selected per matched cell from direct risk score,
weighted sampling, anomaly score, matched KMeans groups, and matched tree
partitions. Uniform sampling is reported but cannot establish a GB contribution.

## Negative results and failures

Failed configurations: {len(failures)}. All per-seed results, including losses,
remain in `cloud_auditing/results.csv` and the append-only experiment JSONL.

## Decision

**{decision}**
"""


if __name__ == "__main__":
    raise SystemExit(main())

