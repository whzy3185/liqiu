"""Summarize raw industrial conventional-ML baselines."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "application_scout" / "raw_baselines.parquet"
REPORT = ROOT / "reports" / "application_scout" / "raw_baselines.md"


def main() -> int:
    frame = pd.read_parquet(SOURCE)
    metrics = ["macro_f1", "balanced_accuracy", "mcc", "minority_recall", "g_mean"]
    summary = frame.groupby(["dataset", "model"])[metrics].agg(["mean", "std"]).round(4)
    winners = (
        frame.groupby(["dataset", "model"], as_index=False).macro_f1.mean()
        .sort_values(["dataset", "macro_f1"], ascending=[True, False])
        .groupby("dataset", as_index=False)
        .first()
    )
    tree_names = ["xgboost", "lightgbm", "catboost", "random_forest", "extra_trees"]
    tree_summary = (
        frame[frame.model.isin(tree_names)]
        .groupby("model")[["macro_f1", "balanced_accuracy", "mcc", "fit_seconds"]]
        .mean()
        .sort_values("macro_f1", ascending=False)
        .round(4)
    )
    diagnostics = (
        frame[frame.model.isin(["knn", "svm_rbf"])]
        .groupby("model")[["macro_f1", "balanced_accuracy", "mcc"]]
        .mean()
        .round(4)
    )
    REPORT.write_text(
        f"""# Raw Industrial Conventional-ML Baselines

## Scope

This first baseline covers three independent real industrial tabular sources:
Steel Plates Faults, SECOM semiconductor yield, and Scania APS failure. It is a
mechanism screen while official mechanical-vibration downloads remain pending;
it cannot by itself satisfy a final fault-diagnosis paper gate.

Five frozen seeds are used. Steel Plates uses seeded stratification, SECOM uses
a chronological split, and APS preserves the official 60k/16k train/test roster.
Every median imputer and scaler is fit on training data only.

KNN and RBF-SVM are diagnostic models and use a stratified 5,000-row fit cap on
larger data. They are not eligible to define the strongest full-data baseline.

## Per-dataset/model metrics

```text
{summary.to_string()}
```

## Strongest model per dataset

```text
{winners.to_string(index=False)}
```

## Tree and boosting comparison

```text
{tree_summary.to_string()}
```

## KNN/SVM diagnostic competitiveness

```text
{diagnostics.to_string()}
```

## Baseline target for GB augmentation

GB structural features and weights must beat the strongest eligible tree or
boosting model **within each matched dataset and seed**. Beating only KNN/SVM
does not count. No large hyperparameter search has been performed at this stage.
""",
        encoding="utf-8",
    )
    print(winners.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

