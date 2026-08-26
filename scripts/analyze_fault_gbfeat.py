"""Apply the preregistered Prompt-8 GO/HOLD/KILL gate."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "application_scout" / "fault_gbfeat.csv"
AUDIT = ROOT / "results" / "application_scout" / "fault_gbfeat_audit.json"
REPORT = ROOT / "reports" / "application_scout" / "fault_gbfeat_decision.md"


def main() -> int:
    frame = pd.read_csv(SOURCE)
    keys = ["dataset", "seed", "model"]
    raw = frame[frame.variant == "raw"].set_index(keys)
    gb = frame[frame.variant == "gbfeat"].set_index(keys)
    paired = gb.join(raw, lsuffix="_gb", rsuffix="_raw", how="inner")
    for metric in ("macro_f1", "balanced_accuracy", "mcc"):
        paired[f"delta_{metric}"] = paired[f"{metric}_gb"] - paired[f"{metric}_raw"]
    dataset_summary = paired.groupby(level="dataset")[[
        "delta_macro_f1", "delta_balanced_accuracy", "delta_mcc"
    ]].agg(["mean", "median", "std"]).round(4)
    delta = paired.delta_macro_f1
    counts = {
        ">0": int((delta > 0).sum()),
        ">=1pp": int((delta >= 0.01).sum()),
        ">=2pp": int((delta >= 0.02).sum()),
        ">=3pp": int((delta >= 0.03).sum()),
        ">=5pp": int((delta >= 0.05).sum()),
        "total": int(len(delta)),
    }
    dataset_means = paired.groupby(level="dataset").delta_macro_f1.mean()
    if len(dataset_means) >= 3 and (dataset_means >= 0.02).sum() >= 3 and dataset_means.max() >= 0.04:
        decision = "GO"
    elif (dataset_means < 0).mean() > 0.5:
        decision = "KILL"
    else:
        decision = "HOLD"
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audit_ok = all(
        fold["disjoint"]
        for item in audit.values()
        for fold in item["folds"]
    )
    REPORT.write_text(
        f"""# Industrial GB Structural-Feature Cheap Test

## Scope

Three independent real industrial tabular sources, five seeds, and five strong
tree/boosting models are compared in matched cells. Training GB features are
5-fold out of fold; validation/test features use a generator fitted only on
training data. OOF audit passed: **{audit_ok}**.

APS generator fitting is capped at a stratified 12,000 training rows per fold
for CPU cost; downstream raw and GBFeat models both use all 48,000 training rows.

## Dataset-level deltas

```text
{dataset_summary.to_string()}
```

## Macro-F1 gain counts

```text
{json.dumps(counts, indent=2)}
```

Overall mean delta: {delta.mean():.4f}; median: {delta.median():.4f};
win/tie/loss: {(delta > 1e-12).sum()}/{(delta.abs() <= 1e-12).sum()}/{(delta < -1e-12).sum()}.

## Resource structure

Mean full generator ball count: {gb.n_balls.mean():.1f}; mean compression ratio:
{gb.compression_ratio.mean():.4f}; mean GB feature time per dataset/seed:
{gb.reset_index().drop_duplicates(['dataset','seed']).gb_feature_seconds.mean():.2f} seconds.

## Gate

`GO` requires all three independent sources to average at least +2pp Macro-F1
and one source to average at least +4pp. A majority of matched declines kills
this feature mechanism.

## Decision

**{decision}**
""",
        encoding="utf-8",
    )
    print(json.dumps({
        "decision": decision,
        "overall_mean_delta": float(delta.mean()),
        "dataset_means": dataset_means.to_dict(),
        **counts,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
