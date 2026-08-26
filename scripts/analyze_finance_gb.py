"""Apply Prompt-15 finance keep/kill thresholds."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "application_scout" / "finance_gb.csv"
AUDIT = ROOT / "results" / "application_scout" / "finance_gb_audit.json"
REPORT = ROOT / "reports" / "application_scout" / "finance_decision.md"


def main() -> int:
    frame = pd.read_csv(SOURCE)
    raw = frame[frame.variant == "raw"].set_index(["dataset", "seed", "model"])
    alternatives = frame[frame.variant != "raw"].copy()
    results = []
    for key, group in alternatives.groupby(["dataset", "seed", "model"]):
        base = raw.loc[key]
        best = group.sort_values(["validation_pr_auc", "validation_roc_auc"], ascending=False).iloc[0]
        results.append({
            "dataset": key[0], "seed": key[1], "model": key[2], "best_variant": best.variant,
            "selection_metric": "validation_pr_auc",
            "delta_pr_auc": best.pr_auc - base.pr_auc,
            "delta_macro_f1": best.macro_f1 - base.macro_f1,
            "delta_mcc": best.mcc - base.mcc,
        })
    paired = pd.DataFrame(results)
    dataset_summary = paired.groupby("dataset")[["delta_pr_auc", "delta_macro_f1", "delta_mcc"]].agg(["mean", "median", "std"]).round(4)
    gains = paired.delta_pr_auc
    dataset_pr = paired.groupby("dataset").delta_pr_auc.mean()
    decision = "GO" if (dataset_pr >= 0.02).sum() >= 3 and dataset_pr.max() >= 0.04 else "KILL"
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    REPORT.write_text(
        f"""# Finance GB Cheap Test

## Scope

Taiwan Default, Australian Credit, and Polish Bankruptcy (5-year horizon) use
five seeded stratified splits. Each cell compares Raw with its stronger of
cross-fitted GB structural features and OOF purity weighting. Thresholds are
selected on validation MCC; PR-AUC remains threshold-free and primary.

OOF audits passed: **{all(value['oof_disjoint'] for value in audit.values())}**.

## Best GB variant versus raw

```text
{dataset_summary.to_string()}
```

Mean PR-AUC delta: {gains.mean():.4f}; median: {gains.median():.4f};
win/tie/loss: {(gains > 1e-12).sum()}/{(gains.abs() <= 1e-12).sum()}/{(gains < -1e-12).sum()}.

## Gate

`GO` requires at least three independent financial datasets with mean PR-AUC or
Macro-F1 gain >= +2pp and at least one >= +4pp. This first screen has exactly
three independent tasks, so all three must meet the +2pp condition.

## Decision

**{decision}**
""",
        encoding="utf-8",
    )
    print(json.dumps({"decision": decision, "dataset_pr_auc_delta": dataset_pr.to_dict(), "mean": float(gains.mean())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
