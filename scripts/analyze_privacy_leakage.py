"""Flatten Cheap Test A records, apply frozen gates, and write the decision report."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "results" / "experiments.jsonl"
CSV = ROOT / "experiments" / "results" / "privacy_leakage_v1.csv"
DIRECTION_CSV = ROOT / "privacy_security" / "results.csv"
REPORT = ROOT / "reports" / "privacy_leakage_cheap_test.md"
ANALYSIS = ROOT / "privacy_security" / "analysis.md"
DECISION = ROOT / "privacy_security" / "decision.md"


def main() -> int:
    records = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    records = [record for record in records if record.get("algorithm") == "privacy-leakage-summary-attack-v1"]
    rows = []
    for record in records:
        if record["outcome"] != "success":
            continue
        for release in record["additional_metrics"]["releases"]:
            row = {
                "experiment_id": record["experiment_id"],
                "dataset": record["dataset"],
                "seed": record["seed"],
                "method": release["method"],
                "variant": release["variant"],
                "n_groups": release["n_groups"],
            }
            row.update(release["metrics"])
            rows.append(row)
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "method", "variant"])
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
    gb = frame[frame.variant == "R8_center_radius_count_purity"].set_index(["dataset", "seed"])
    km = frame[frame.variant == "R4_center_radius_count"].set_index(["dataset", "seed"])
    paired = gb.join(km, lsuffix="_gb", rsuffix="_km", how="inner")
    auc_delta = paired.membership_roc_auc_gb - paired.membership_roc_auc_km
    utility_delta = paired.utility_accuracy_gb - paired.utility_accuracy_km
    privacy_wins = (auc_delta <= -0.03) & (utility_delta >= -0.02)
    leakage_signal = (
        (
            (paired.ball_size_attack_spearman_gb <= -0.25)
            & (
                paired.ball_size_attack_spearman_gb
                <= paired.ball_size_attack_spearman_km - 0.15
            )
        )
        | (
            (paired.purity_attack_spearman_gb >= 0.25)
            & (
                paired.purity_attack_spearman_gb
                >= paired.purity_attack_spearman_km + 0.15
            )
        )
    ).fillna(False)
    evidence = {
        "paired_runs": int(len(paired)),
        "mean_membership_auc_delta_gb_minus_kmeans": float(auc_delta.mean()),
        "mean_utility_delta_gb_minus_kmeans": float(utility_delta.mean()),
        "privacy_win_fraction": float(privacy_wins.mean()),
        "gb_specific_leakage_fraction": float(leakage_signal.mean()),
    }
    if len(paired) >= 20 and privacy_wins.mean() >= 0.8:
        return "GO", evidence
    if len(paired) >= 20 and leakage_signal.mean() >= 0.7:
        return "GO", evidence
    if len(paired) >= 20 and np.abs(auc_delta).mean() < 0.02:
        return "KILL", evidence
    return "HOLD", evidence


def _report(frame: pd.DataFrame, records: list[dict], decision: str, evidence: dict) -> str:
    failures = [record for record in records if record["outcome"] != "success"]
    metrics = [
        "membership_roc_auc",
        "attribute_accuracy",
        "reconstruction_mse",
        "utility_accuracy",
        "compression_ratio",
    ]
    summary = (
        frame.groupby(["method", "variant"])[metrics]
        .agg(["mean", "std"])
        .round(4)
        .reset_index()
    )
    summary.columns = ["_".join(part for part in column if part) for column in summary.columns]
    summary_text = summary.to_string(index=False)
    return f"""# Privacy Leakage Cheap Test A

## Scope

Five exploration datasets, five frozen seeds, CPU-only execution, and matched
representative counts. Membership results come from a cross-validated attack on
distance and only the statistics actually disclosed by each R0-R8 release.
These are empirical leakage measurements, not formal privacy guarantees.

## Aggregate results

```text
{summary_text}
```

## GB-specific gate

- Paired GB-vs-KMeans runs: {evidence['paired_runs']}
- Mean membership AUC delta (GB minus KMeans): {evidence['mean_membership_auc_delta_gb_minus_kmeans']:.4f}
- Mean utility accuracy delta (GB minus KMeans): {evidence['mean_utility_delta_gb_minus_kmeans']:.4f}
- Fraction meeting the frozen privacy win rule: {evidence['privacy_win_fraction']:.3f}
- Fraction showing the predeclared small/high-purity ball leakage pattern: {evidence['gb_specific_leakage_fraction']:.3f}

## Negative results and failures

Failed configurations: {len(failures)}. They remain in the append-only JSONL.
All non-winning releases remain in `experiments/results/privacy_leakage_v1.csv`.

## Strongest competing explanation

Any gain may be caused by lossy prototype release, supervised partitioning, or
the number of representatives. The primary decision therefore uses the
same-count KMeans comparator; random, hierarchical, tree, and raw releases are
diagnostic controls rather than weak foils.

## Decision

**{decision}**
"""


if __name__ == "__main__":
    raise SystemExit(main())
