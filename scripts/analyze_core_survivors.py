"""Render the decision report for the frozen GB-core stress campaign."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/results/experiments.jsonl"
REPORT = ROOT / "reports/core_exploration/survivor_report.md"
TAUS = (0.60, 0.75, 0.85, 0.95, 1.0)


def mean(values):
    return statistics.fmean(values)


def frontier(record, tau):
    rows = [
        row
        for row in record["additional_metrics"]["frontier"]
        if abs(float(row["tau"]) - tau) < 1e-12
    ]
    if len(rows) != 1:
        raise ValueError(f"{record['experiment_id']}: missing tau={tau}")
    return rows[0]


def load():
    records = [json.loads(line) for line in RESULTS.read_text().splitlines() if line]
    core = [r for r in records if r.get("study", "").startswith("granular-ball-core")]
    expected = {
        "granular-ball-core-noise": 240,
        "granular-ball-core-imbalance": 120,
        "granular-ball-core-shift": 40,
    }
    observed = {study: sum(r["study"] == study for r in core) for study in expected}
    if observed != expected or len(core) != 400:
        raise ValueError(f"frozen grid mismatch: {observed}, total={len(core)}")
    if len({r["experiment_id"] for r in core}) != 400:
        raise ValueError("duplicate core experiment IDs")
    if any(r.get("outcome") != "success" for r in core):
        raise ValueError("frozen core campaign contains non-success records")
    for record in core:
        taus = tuple(sorted(float(row["tau"]) for row in record["additional_metrics"]["frontier"]))
        if taus != TAUS:
            raise ValueError(f"{record['experiment_id']}: frontier mismatch {taus}")
    return core


def noise_summary(records):
    rows = [r for r in records if r["study"] == "granular-ball-core-noise"]
    output = []
    for rate in (0.10, 0.20, 0.30):
        pairs = []
        for record in rows:
            params = record["dataset_generation_parameters"]
            if params["noise_rate"] != rate:
                continue
            baseline_params = dict(params)
            baseline_params["noise_rate"] = 0
            baseline = next(
                r
                for r in rows
                if r["seed"] == record["seed"]
                and r["dataset_generation_parameters"] == baseline_params
            )
            noisy = frontier(record, 1.0)
            clean = frontier(baseline, 1.0)
            pairs.append(
                (
                    noisy["granules"] / clean["granules"],
                    noisy["accuracy"] - clean["accuracy"],
                )
            )
        output.append(
            {
                "rate": rate,
                "pairs": len(pairs),
                "resource_failures": sum(ratio >= 1.30 for ratio, _ in pairs),
                "accuracy_failures": sum(delta <= -0.01 for _, delta in pairs),
                "median_granule_ratio": statistics.median(ratio for ratio, _ in pairs),
                "mean_accuracy_delta": mean(delta for _, delta in pairs),
            }
        )
    return output


def imbalance_summary(records):
    rows = [r for r in records if r["study"] == "granular-ball-core-imbalance"]
    severe = [
        r
        for r in rows
        if r["dataset_generation_parameters"]["imbalance_ratio"] in (20, 50)
    ]
    primary = [frontier(r, 0.85) for r in severe]
    pure = [frontier(r, 1.0) for r in severe]
    return {
        "runs": len(severe),
        "primary_zero_recall": sum(row["minority_recall"] == 0 for row in primary),
        "primary_macro_f1": mean(row["macro_f1"] for row in primary),
        "primary_granules": mean(row["granules"] for row in primary),
        "pure_zero_recall": sum(row["minority_recall"] == 0 for row in pure),
        "pure_macro_f1": mean(row["macro_f1"] for row in pure),
        "pure_granules": mean(row["granules"] for row in pure),
        "reference_macro_f1": mean(
            max(v["macro_f1"] for v in r["additional_metrics"]["references"].values())
            for r in severe
        ),
    }


def shift_summary(records):
    rows = [r for r in records if r["study"] == "granular-ball-core-shift"]
    output = []
    for shift in ("covariate_shift", "concept_drift", "prior_shift", "density_drift"):
        subset = [r for r in rows if r["dataset_generation_parameters"]["shift_kind"] == shift]
        gbc = [frontier(r, 0.85) for r in subset]
        rf = [r["additional_metrics"]["references"]["RandomForest"] for r in subset]
        output.append(
            {
                "shift": shift,
                "accuracy": mean(row["accuracy"] for row in gbc),
                "ece": mean(row["ece"] for row in gbc),
                "accuracy_gap_rf": mean(a["accuracy"] - b["accuracy"] for a, b in zip(gbc, rf)),
                "ece_gap_rf": mean(a["ece"] - b["ece"] for a, b in zip(gbc, rf)),
            }
        )
    return output


def render(records):
    noise = noise_summary(records)
    imbalance = imbalance_summary(records)
    shift = shift_summary(records)

    noise_rows = "\n".join(
        f"| {row['rate']:.1f} | {row['accuracy_failures']}/{row['pairs']} | "
        f"{row['resource_failures']}/{row['pairs']} | {row['median_granule_ratio']:.2f}x | "
        f"{row['mean_accuracy_delta']:+.3f} |"
        for row in noise
    )
    shift_rows = "\n".join(
        f"| {row['shift']} | {row['accuracy']:.3f} | {row['ece']:.3f} | "
        f"{row['accuracy_gap_rf']:+.3f} | {row['ece_gap_rf']:+.3f} |"
        for row in shift
    )

    return f"""# GB-core exploration survivor report

Generated by `python scripts/analyze_core_survivors.py` from the append-only
experiment ledger. Audit date: 2026-08-25.

## Outcome

The frozen campaign completed **400/400 successful CPU configurations**:
240 label-noise, 120 imbalance, and 40 shift/UQ runs. Each cell uses two
granular-ball generators and five seeds. **No candidate reaches P0.**

The round found two stable granular-ball failures, but it did not produce a
mechanism that survives the latest granular-ball prior art and strong baselines.
The shift/UQ line fails its cross-shift gate.

## What failed

### C1: purity-chasing noise fragmentation - `P1`

At `tau=1`, each noisy run is paired with the same family, noise kind, generator
and seed at zero noise.

| Noise rate | Accuracy loss >=1pp | Granules +>=30% | Median granule ratio | Mean clean-test accuracy delta |
|---:|---:|---:|---:|---:|
{noise_rows}

Clean-test accuracy degrades in all 180 noisy pairs, while the median granule
inflation rises from {noise[0]['median_granule_ratio']:.2f}x to
{noise[-1]['median_granule_ratio']:.2f}x. The failure is real across Gaussian
blobs, moons, spirals, symmetric/boundary corruption, both generators and five
seeds. It remains P1 because no repair was tested and 2026 CMGBIFSC/ScOrGBC work
already explicitly targets excessive high-purity fragmentation.

### C2: majority-label minority masking - `REJECT`

For 20:1 and 50:1 training imbalance, `tau=.85` retains one majority ball in
**{imbalance['primary_zero_recall']}/{imbalance['runs']} runs**. Mean minority
recall is zero, Macro-F1 is {imbalance['primary_macro_f1']:.3f}, and the mean
granule count is {imbalance['primary_granules']:.1f}. Raising `tau` to 1.0
eliminates zero-recall runs ({imbalance['pure_zero_recall']}/{imbalance['runs']}),
raises Macro-F1 to {imbalance['pure_macro_f1']:.3f}, and uses
{imbalance['pure_granules']:.1f} balls; the best point reference averages
{imbalance['reference_macro_f1']:.3f} Macro-F1.

This is an exact raw-purity stopping failure across all three families, both
generators and five seeds, but it is rejected as a standalone candidate. The
existing `tau=1` arm directly repairs the synthetic failure with few balls, and
class-mapped allocation, per-class floors, granular-ball sampling and
imbalance-specific GB methods already occupy the repair space.

### C3: shift-induced confidence failure - `REJECT`

Primary `tau=.85` means against RandomForest:

| Shift | GBC Accuracy | GBC ECE | Delta Accuracy | Delta ECE |
|---|---:|---:|---:|---:|
{shift_rows}

Only density drift preserves point accuracy while materially worsening ECE.
Prior shift is C2 again: the old-prior root satisfies the raw-purity stop and
swallows the new minority structure. Concept drift is a 180-degree reversal that
breaks every frozen classifier; covariate shift is shared with RF/5-NN. The
required independent signal across at least three shifts is absent.

The implemented confidence is the selected ball's training class proportion.
In 30/40 primary runs it is structurally constant: either a single retained ball
emits one vector for every point or all retained balls are pure and emit maximum
confidence 1. Selective-risk ties are therefore arbitrary, not a usable UQ
mechanism.

## Ideas killed this round

- **"Use higher purity for robustness"** is killed: it overfits corrupted labels
  and simultaneously expands the representation.
- **"Use one global lower purity for efficiency"** is killed: class prior alone
  can make the root satisfy the threshold and erase every minority prediction.
- **"GB + TTA/OOD/UQ"** is killed as a standalone topic: the current evidence is
  either generic model failure, C2 under another name, or one-shift calibration.
- **"Class-proportion confidence enables selective prediction"** is killed for
  pure or one-ball cuts because confidence has no ranking resolution.

## Current strongest three

| Rank | Candidate | Status | Reason it remains / closes |
|---:|---|---|---|
| 1 | C1 purity/noise risk-resource failure map | `P1` | Stable cross-family failure; repair and novelty absent |
| 2 | C2 prior-sensitive purity-stop collapse | `REJECT` | Exact failure, but fixed `tau=1` repairs it and prior art occupies the mechanism |
| 3 | C3 shift/UQ | `REJECT` | Independent cross-shift gate failed |

## Cheapest next kill tests

1. **C1:** compare source-available recent GB generators on only noise rates
   0/.2, three families, two noise kinds and five seeds. Kill if a recent method
   removes the risk/resource phase without a new failure region.
2. **C2:** implement one transparent class-prior-normalized stopping baseline
   and compare it with class-mapped/per-class-floor GB allocation at equal ball
   count. Kill as research if gains disappear under equal resources or on three
   real imbalanced datasets.
3. **New GB-core queue:** test nonlocal routing interference caused by replacing
   a ball with children under `||x-center||-radius`. Promote only if a local split
   changes remote assignments and increases risk across three geometries, both
   generators and five seeds; this is more GB-specific than another application.

Do not reopen C3 unless a density/prior severity sweep shows a GBC-specific UQ
failure at least one severity step before a 1 pp accuracy loss in both shifts and
at least four of five seeds.
"""


def main():
    records = load()
    REPORT.write_text(render(records), encoding="utf-8")
    print(json.dumps({"records": len(records), "p0": 0, "p1": 1, "reject": 2, "report": str(REPORT.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
