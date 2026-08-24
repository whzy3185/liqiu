"""Audit the frozen granular-ball shift/UQ stress batch and render its report."""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/results/experiments.jsonl"
REPORT = ROOT / "reports/core_exploration/shift_report.md"
STUDY = "granular-ball-core-shift"
SHIFTS = ("covariate_shift", "concept_drift", "prior_shift", "density_drift")
METHODS = ("kmeans", "class_means")
SEEDS = (1, 7, 21, 42, 2026)
TAUS = (0.60, 0.75, 0.85, 0.95, 1.0)
PRIMARY_TAU = 0.85
REFERENCES = ("RandomForest", "RBF-SVM", "5-NN")
COVERAGES = (0.5, 0.7, 0.9)
METRICS = ("accuracy", "ece", "brier", "nll")


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else math.nan


def pstdev(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def fmt(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "NA"
    return f"{value:.{digits}f}"


def signed(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "NA"
    return f"{value:+.{digits}f}"


def percentage(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}%"


def selective_risk(metrics: dict[str, Any], coverage: float) -> float:
    for point in metrics["selective"]:
        if math.isclose(float(point["coverage"]), coverage, abs_tol=1e-12):
            return float(point["selective_risk"])
    raise ValueError(f"missing selective-risk coverage {coverage}")


def selective_threshold(metrics: dict[str, Any], coverage: float) -> float:
    for point in metrics["selective"]:
        if math.isclose(float(point["coverage"]), coverage, abs_tol=1e-12):
            return float(point["threshold"])
    raise ValueError(f"missing selective-risk coverage {coverage}")


def primary(record: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row
        for row in record["additional_metrics"]["frontier"]
        if math.isclose(float(row["tau"]), PRIMARY_TAU, abs_tol=1e-12)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{record['experiment_id']}: expected one tau={PRIMARY_TAU} row"
        )
    return matches[0]


def load_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with RESULTS.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
            if record.get("study") == STUDY:
                records.append(record)

    if len(records) != 40:
        raise ValueError(f"expected exactly 40 frozen {STUDY} records, got {len(records)}")
    if any(record.get("outcome") != "success" for record in records):
        failed = [
            record.get("experiment_id")
            for record in records
            if record.get("outcome") != "success"
        ]
        raise ValueError(f"non-success records in frozen batch: {failed}")

    ids = [record["experiment_id"] for record in records]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate experiment_id in frozen shift batch")

    expected = {
        (shift, method, seed)
        for shift in SHIFTS
        for method in METHODS
        for seed in SEEDS
    }
    observed = {
        (
            record["dataset_generation_parameters"]["shift_kind"],
            record["dataset_generation_parameters"]["generation_method"],
            int(record["seed"]),
        )
        for record in records
    }
    if observed != expected:
        raise ValueError(
            f"frozen grid mismatch: missing={sorted(expected-observed)}, "
            f"unexpected={sorted(observed-expected)}"
        )

    for record in records:
        frontier = record["additional_metrics"]["frontier"]
        observed_taus = tuple(sorted(float(row["tau"]) for row in frontier))
        if observed_taus != TAUS:
            raise ValueError(
                f"{record['experiment_id']}: expected taus {TAUS}, got {observed_taus}"
            )
        if set(record["additional_metrics"]["references"]) != set(REFERENCES):
            raise ValueError(f"{record['experiment_id']}: reference set mismatch")
        for metrics in [*frontier, *record["additional_metrics"]["references"].values()]:
            for metric in METRICS:
                if metric not in metrics or not math.isfinite(float(metrics[metric])):
                    raise ValueError(
                        f"{record['experiment_id']}: missing/nonfinite {metric}"
                    )
            for coverage in COVERAGES:
                selective_risk(metrics, coverage)

    return sorted(
        records,
        key=lambda record: (
            SHIFTS.index(record["dataset_generation_parameters"]["shift_kind"]),
            METHODS.index(record["dataset_generation_parameters"]["generation_method"]),
            SEEDS.index(int(record["seed"])),
        ),
    )


def filter_records(
    records: list[dict[str, Any]], shift: str | None = None, method: str | None = None
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if (shift is None or record["dataset_generation_parameters"]["shift_kind"] == shift)
        and (
            method is None
            or record["dataset_generation_parameters"]["generation_method"] == method
        )
    ]


def primary_value(record: dict[str, Any], metric: str) -> float:
    if metric.startswith("sel"):
        return selective_risk(primary(record), float(metric.removeprefix("sel")) / 100)
    return float(primary(record)[metric])


def reference_value(record: dict[str, Any], reference: str, metric: str) -> float:
    values = record["additional_metrics"]["references"][reference]
    if metric.startswith("sel"):
        return selective_risk(values, float(metric.removeprefix("sel")) / 100)
    return float(values[metric])


def deltas(
    records: list[dict[str, Any]], reference: str, metric: str
) -> list[float]:
    return [
        primary_value(record, metric) - reference_value(record, reference, metric)
        for record in records
    ]


def cell_groups(records: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[
            (
                record["dataset_generation_parameters"]["shift_kind"],
                record["dataset_generation_parameters"]["generation_method"],
            )
        ].append(record)
    return groups


def confidence_before_accuracy_proxy(
    record: dict[str, Any], reference: str
) -> bool:
    """Endpoint proxy, not a longitudinal before/after claim.

    Accuracy is noninferior within one percentage point while either ECE or
    selective risk at 50% coverage is at least five points worse.
    """

    accuracy_noninferior = deltas([record], reference, "accuracy")[0] >= -0.01
    uq_worse = (
        deltas([record], reference, "ece")[0] >= 0.05
        or deltas([record], reference, "sel50")[0] >= 0.05
    )
    return accuracy_noninferior and uq_worse


def is_provably_constant_confidence(record: dict[str, Any]) -> bool:
    row = primary(record)
    # One retained ball emits one probability vector for all x. If every
    # retained ball is pure, every prediction has max class probability one.
    return int(row["granules"]) == 1 or math.isclose(
        float(row["mean_purity"]), 1.0, abs_tol=1e-12
    )


def frontier_ranges(record: dict[str, Any]) -> dict[str, float]:
    frontier = record["additional_metrics"]["frontier"]
    out: dict[str, float] = {}
    for metric in ("accuracy", "ece", "brier", "nll"):
        values = [float(row[metric]) for row in frontier]
        out[f"{metric}_range"] = max(values) - min(values)
    for coverage in COVERAGES:
        values = [selective_risk(row, coverage) for row in frontier]
        out[f"sel{int(coverage*100)}_range"] = max(values) - min(values)
    granules = [int(row["granules"]) for row in frontier]
    out["granule_range"] = float(max(granules) - min(granules))
    p = primary(record)
    out["primary_accuracy_regret"] = max(
        float(row["accuracy"]) for row in frontier
    ) - float(p["accuracy"])
    out["primary_ece_regret"] = float(p["ece"]) - min(
        float(row["ece"]) for row in frontier
    )
    out["primary_brier_regret"] = float(p["brier"]) - min(
        float(row["brier"]) for row in frontier
    )
    out["primary_nll_regret"] = float(p["nll"]) - min(
        float(row["nll"]) for row in frontier
    )
    out["primary_accuracy_best_tie"] = float(
        math.isclose(
            float(p["accuracy"]),
            max(float(row["accuracy"]) for row in frontier),
            abs_tol=1e-12,
        )
    )
    out["primary_ece_best_tie"] = float(
        math.isclose(
            float(p["ece"]),
            min(float(row["ece"]) for row in frontier),
            abs_tol=1e-12,
        )
    )
    return out


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(records: list[dict[str, Any]]) -> str:
    cells = cell_groups(records)

    absolute_rows: list[list[str]] = []
    for shift in SHIFTS:
        for method in METHODS:
            group = cells[(shift, method)]
            absolute_rows.append(
                [
                    shift,
                    method,
                    fmt(mean(primary_value(record, "accuracy") for record in group)),
                    fmt(mean(primary_value(record, "ece") for record in group)),
                    fmt(mean(primary_value(record, "brier") for record in group)),
                    fmt(mean(primary_value(record, "nll") for record in group)),
                    fmt(mean(primary_value(record, "sel50") for record in group)),
                    fmt(mean(float(primary(record)["granules"]) for record in group), 1),
                ]
            )

    delta_rows: list[list[str]] = []
    for shift in SHIFTS:
        group = filter_records(records, shift=shift)
        for reference in REFERENCES:
            delta_rows.append(
                [
                    shift,
                    reference,
                    signed(mean(deltas(group, reference, "accuracy"))),
                    signed(mean(deltas(group, reference, "ece"))),
                    signed(mean(deltas(group, reference, "brier"))),
                    signed(mean(deltas(group, reference, "nll"))),
                    signed(mean(deltas(group, reference, "sel50"))),
                ]
            )

    stability_rows: list[list[str]] = []
    for reference in REFERENCES:
        proxy_runs = sum(
            confidence_before_accuracy_proxy(record, reference) for record in records
        )
        stable_cells = sum(
            sum(confidence_before_accuracy_proxy(record, reference) for record in group)
            >= 4
            for group in cells.values()
        )
        degraded_shifts: list[str] = []
        proxy_shifts: list[str] = []
        for shift in SHIFTS:
            group = filter_records(records, shift=shift)
            uq_worse = (
                mean(deltas(group, reference, "ece")) >= 0.05
                or mean(deltas(group, reference, "sel50")) >= 0.05
            )
            acc_noninferior = mean(deltas(group, reference, "accuracy")) >= -0.01
            if uq_worse:
                degraded_shifts.append(shift)
            if uq_worse and acc_noninferior:
                proxy_shifts.append(shift)
        stability_rows.append(
            [
                reference,
                f"{proxy_runs}/40",
                f"{stable_cells}/8",
                ", ".join(degraded_shifts) or "none",
                ", ".join(proxy_shifts) or "none",
            ]
        )

    sensitivity_rows: list[list[str]] = []
    for shift in SHIFTS:
        for method in METHODS:
            group = cells[(shift, method)]
            ranges = [frontier_ranges(record) for record in group]
            sensitivity_rows.append(
                [
                    shift,
                    method,
                    fmt(mean(row["accuracy_range"] for row in ranges)),
                    fmt(mean(row["ece_range"] for row in ranges)),
                    fmt(mean(row["nll_range"] for row in ranges)),
                    fmt(mean(row["sel50_range"] for row in ranges)),
                    fmt(mean(row["granule_range"] for row in ranges), 1),
                    fmt(mean(row["primary_accuracy_regret"] for row in ranges)),
                    fmt(mean(row["primary_ece_regret"] for row in ranges)),
                ]
            )

    tau_rows: list[list[str]] = []
    for shift in SHIFTS:
        group = filter_records(records, shift=shift)
        row = [shift]
        for tau in TAUS:
            points = [
                next(
                    point
                    for point in record["additional_metrics"]["frontier"]
                    if math.isclose(float(point["tau"]), tau, abs_tol=1e-12)
                )
                for record in group
            ]
            row.append(
                f"{fmt(mean(float(point['accuracy']) for point in points))}/"
                f"{fmt(mean(float(point['ece']) for point in points))}/"
                f"{fmt(mean(float(point['granules']) for point in points), 1)}"
            )
        tau_rows.append(row)

    constant_records = [record for record in records if is_provably_constant_confidence(record)]
    constant_by_shift = {
        shift: sum(
            is_provably_constant_confidence(record)
            for record in filter_records(records, shift=shift)
        )
        for shift in SHIFTS
    }
    pure_records = [
        record
        for record in records
        if math.isclose(float(primary(record)["mean_purity"]), 1.0, abs_tol=1e-12)
    ]
    one_ball_records = [record for record in records if int(primary(record)["granules"]) == 1]
    tie90_records = [
        record
        for record in records
        if math.isclose(selective_threshold(primary(record), 0.9), 1.0, abs_tol=1e-12)
    ]

    density = filter_records(records, shift="density_drift")
    density_full_risk = mean(1 - primary_value(record, "accuracy") for record in density)
    density_sel50 = mean(primary_value(record, "sel50") for record in density)
    density_ref_ranking = {
        reference: (
            mean(1 - reference_value(record, reference, "accuracy") for record in density),
            mean(reference_value(record, reference, "sel50") for record in density),
        )
        for reference in REFERENCES
    }

    range_rows = [frontier_ranges(record) for record in records]
    sensitive_accuracy = sum(row["accuracy_range"] >= 0.01 for row in range_rows)
    sensitive_ece = sum(row["ece_range"] >= 0.02 for row in range_rows)
    primary_acc_best = sum(row["primary_accuracy_best_tie"] for row in range_rows)
    primary_ece_best = sum(row["primary_ece_best_tie"] for row in range_rows)

    method_differences: list[float] = []
    for shift in SHIFTS:
        for seed in SEEDS:
            kmeans_record = next(
                record
                for record in records
                if record["dataset_generation_parameters"]["shift_kind"] == shift
                and record["dataset_generation_parameters"]["generation_method"] == "kmeans"
                and int(record["seed"]) == seed
            )
            class_means_record = next(
                record
                for record in records
                if record["dataset_generation_parameters"]["shift_kind"] == shift
                and record["dataset_generation_parameters"]["generation_method"]
                == "class_means"
                and int(record["seed"]) == seed
            )
            method_differences.append(
                abs(
                    primary_value(kmeans_record, "accuracy")
                    - primary_value(class_means_record, "accuracy")
                )
            )

    return f"""# Granular-ball core shift and uncertainty audit

Generated by `python3 scripts/analyze_core_shift.py` from the append-only
experiment ledger. Audit date: 2026-08-25.

## Decision

**`REJECT` C3 as a standalone cross-shift research candidate.** Retain the
result as an engineering warning and mechanism note, not as P0/P1 paper scope.

The frozen batch does expose a concrete defect: at the primary `tau=.85`,
nearest-ball class proportions are provably constant as confidence scores in
**{len(constant_records)}/40 runs ({percentage(len(constant_records)/40)})**.
That includes {len(pure_records)} runs where every retained ball is pure and
therefore every prediction has confidence 1, plus {len(one_ball_records)} runs
where one root ball emits the same probability vector for every test point.
This degeneracy covers {constant_by_shift['covariate_shift']}/10 covariate,
{constant_by_shift['prior_shift']}/10 prior, and
{constant_by_shift['density_drift']}/10 density runs. It is a valid limitation
of the implemented confidence, but not a new uncertainty-under-shift result.

The preregistered candidate gate required ECE/selective-risk degradation across
at least three shifts before or with accuracy loss. Against RandomForest and
RBF-SVM, material endpoint UQ degradation appears in only two shifts
(`density_drift`, `prior_shift`); against 5-NN it appears materially in only
`prior_shift`. Only density drift shows the desired decoupling of competitive
accuracy from worse UQ. The experiment also observes only `t=9`, so temporal
"confidence fails before accuracy" is not identifiable.

## Frozen evidence and audit rules

- Exactly 40 successful unique records were required: 4 shifts x 2 granular-
  ball generators x 5 seeds (`1, 7, 21, 42, 2026`).
- Train is stream batch `t=0`; evaluation is final batch `t=9`, 300 examples
  each. No intermediate batch is stored.
- The primary GBC cut is the runner's frozen `tau=.85`. Purity sensitivity uses
  all five frozen thresholds `.60, .75, .85, .95, 1.0`.
- Deltas below are `GBC - reference`. Positive is favorable only for Accuracy;
  negative is favorable for ECE, Brier, NLL, and selective risk.
- Selective risk is error among the highest-confidence 50%, 70%, or 90%.
- The audit-only endpoint proxy for "confidence-before-accuracy" requires GBC
  Accuracy no worse than 1 pp relative to a comparator while ECE or selective
  risk at 50% coverage is at least 5 pp worse. These thresholds were not
  preregistered and do not turn an endpoint comparison into a temporal result.

The script fails closed if the record count, outcome, grid, references, tau set,
or required metrics differ. It never writes the JSONL.

## Primary GBC endpoint performance

Means over five seeds. `SelR50` is selective risk at 50% coverage.

{markdown_table(
    ['Shift', 'Method', 'Accuracy', 'ECE', 'Brier', 'NLL', 'SelR50', 'Granules'],
    absolute_rows,
)}

The two generation methods are not independent confirmations at the primary
cut: paired mean absolute Accuracy difference is only
{fmt(mean(method_differences), 4)} across 20 shift-seed pairs, and all primary
means outside concept drift are identical. In the easy separable training batch,
both methods commonly stop at the same root or two pure children.

## Relative to RF, RBF-SVM, and 5-NN

Each row averages both generators and all five seeds for the named shift.

{markdown_table(
    ['Shift', 'Reference', 'Delta Acc', 'Delta ECE', 'Delta Brier', 'Delta NLL', 'Delta SelR50'],
    delta_rows,
)}

The main attribution is shift-specific:

- **Density drift is the only confidence/accuracy decoupling signal.** GBC mean
  Accuracy is {fmt(mean(primary_value(r, 'accuracy') for r in density))}; it is
  {signed(mean(deltas(density, 'RandomForest', 'accuracy')))} vs RF and
  {signed(mean(deltas(density, 'RBF-SVM', 'accuracy')))} vs RBF-SVM. Yet ECE is
  worse by {signed(mean(deltas(density, 'RandomForest', 'ece')))} and
  {signed(mean(deltas(density, 'RBF-SVM', 'ece')))}, while NLL is worse by
  {signed(mean(deltas(density, 'RandomForest', 'nll')))} and
  {signed(mean(deltas(density, 'RBF-SVM', 'nll')))}. This is stable evidence
  that pure-ball proportions are not useful posterior confidence under overlap.
- **Prior shift is a purity-stop failure with simultaneous point failure.**
  Training class-1 prior moves from `.1` to `.9`; `tau=.85` retains one old-
  majority root ball. GBC Accuracy is about .117 versus .998-.999 for all three
  references, while ECE is .782. This does not establish confidence failing
  first.
- **Concept drift is a generic 180-degree label-boundary reversal.** All
  baselines collapse to roughly 0-3% Accuracy with ECE near 1. GBC being
  slightly less bad is not a granular-ball advantage.
- **Covariate shift is also not a clean GBC-specific win.** GBC, RF, and 5-NN
  all end near .476 Accuracy. Pure GBC balls still emit confidence 1, but RF has
  nearly the same endpoint ECE; RBF-SVM is substantially worse here.

## Did confidence fail before accuracy?

Not longitudinally answerable. The frozen records contain only the final batch.
The endpoint proxy gives:

{markdown_table(
    ['Reference', 'Proxy-positive runs', 'Stable cells (>=4/5)', 'UQ-degraded shifts', 'Accuracy-preserved UQ shifts'],
    stability_rows,
)}

Thus the strongest allowed statement is: **under density drift, GBC point
accuracy remains competitive while its class-proportion confidence is worse
than RF/RBF-SVM by proper scoring and selective ranking.** The data do not show
that calibration deteriorates at an earlier time or lower shift severity.

## Selective-risk audit

The density result is particularly revealing. GBC full risk is
{fmt(density_full_risk)}, and retaining the nominal top-confidence 50% yields
risk {fmt(density_sel50)}, only {fmt(density_full_risk-density_sel50)} lower.
The corresponding full-risk to SelR50 changes are:

{markdown_table(
    ['Model', 'Full risk', 'SelR50', 'Risk reduction'],
    [['GBC tau=.85', fmt(density_full_risk), fmt(density_sel50), fmt(density_full_risk-density_sel50)]]
    + [
        [reference, fmt(values[0]), fmt(values[1]), fmt(values[0]-values[1])]
        for reference, values in density_ref_ranking.items()
    ],
)}

However, this is not a valid GBC ranking gain: all density-drift primary cuts
have pure balls, so every max class probability is exactly 1. `argsort` breaks
ties by sample order, making coverage subsets arbitrary. Across the full batch,
{len(tie90_records)}/40 runs still have confidence threshold 1 at 90% coverage.
Risk-coverage numbers must therefore be accompanied by tie diagnostics; without
them they can falsely look like selective prediction.

## Purity sensitivity

Mean within-run range over the five tau values. `AccRegret85` is best frontier
Accuracy minus Accuracy at `.85`; `ECERegret85` is ECE at `.85` minus best
frontier ECE.

{markdown_table(
    ['Shift', 'Method', 'Acc range', 'ECE range', 'NLL range', 'SelR50 range', 'Granule range', 'AccRegret85', 'ECERegret85'],
    sensitivity_rows,
)}

Compact frontier means are `Accuracy/ECE/granules`, averaged over both methods
and all five seeds:

{markdown_table(
    ['Shift'] + [f'tau={tau:g}' for tau in TAUS],
    tau_rows,
)}

Across all 40 runs, {sensitive_accuracy}/40 have at least 1 pp Accuracy range and
{sensitive_ece}/40 have at least 2 pp ECE range. The frozen `.85` cut ties for
best Accuracy in {int(primary_acc_best)}/40 runs and best ECE in
{int(primary_ece_best)}/40. Sensitivity is concentrated in prior shift and
concept drift; covariate and density results are flat because both generators
already expose two pure leaves over most/all thresholds. This is another reason
not to describe five tau values as five independent uncertainty mechanisms.

## Why nearest-ball class-proportion is not uncertainty

The implementation uses the training label counts of the selected ball as
`predict_proba`, then routes each test point to the ball minimizing
`||x-center|| - radius`. This has six limitations:

1. The class proportion estimates `P_train(Y | assigned ball)`, not
   `P_test(Y | X=x)`. Prior, concept, and conditional shifts invalidate the
   identification immediately.
2. Radius affects which ball wins but never discounts confidence for a point far
   outside training support. There is no epistemic/OOD term.
3. Overlapping balls and nearest-surface routing can assign a point to a ball
   whose training membership did not contain comparable points.
4. Pure leaves emit exact 0/1 probabilities. One error then receives a clipped
   log penalty, explaining NLL values far worse than ECE alone suggests.
5. A one-ball cut emits the same probability for every point. A pure multi-ball
   cut emits the same maximum confidence for every point. Neither can rank
   abstention decisions even when its point labels are useful.
6. ECE with ten fixed bins on 300 shifted examples is a coarse sample statistic,
   not a calibration guarantee. Brier and NLL are proper scores, but they also
   require an honest target distribution and uncertainty intervals.

The references are not gold-standard UQ methods either. RF and 5-NN use native
class-frequency probabilities; `SVC(probability=True)` uses fitted probability
scaling. Their role here is attribution at equal frozen data, not proof of
calibration under shift.

## Collision and attribution audit

- The broad claim that predictive uncertainty and calibration degrade under
  dataset shift is already directly occupied by Ovadia et al.,
  [NeurIPS 2019](https://proceedings.neurips.cc/paper_files/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html).
- Risk-coverage/selective prediction is established methodology; confidence-
  threshold rejection is explicitly the baseline discussed by Geifman and
  El-Yaniv, [ICML 2019](https://proceedings.mlr.press/v97/geifman19a.html).
- Using relative class frequency in a tree leaf as probability is standard, and
  dedicated calibration methods exist. See Johansson et al.,
  [Venn Predictors for Well-Calibrated Probability Estimation Trees](https://proceedings.mlr.press/v91/johansson18a/johansson18a.pdf),
  and Niculescu-Mizil and Caruana,
  [ICML 2005](https://doi.org/10.1145/1102351.1102430).
- The repository's prior granular-ball gap scan found adjacent GB work on open
  intent/OOD noise, continual and incremental learning, fuzzy uncertainty, and
  entropy-based uncertainty. An exact static nearest-ball shift-calibration
  study remains less crowded, but "GBC + shift/UQ" is not a mechanism claim.

**Attribution verdict:** prior-shift collapse is caused by the global purity
stop retaining the stale old-prior root; density-drift UQ failure is caused by
pure training leaves outputting certainty despite class overlap; concept-drift
collapse is generic to all frozen classifiers; covariate-shift failure is also
shared by RF/5-NN. Only the first two are meaningfully GBC-specific, and neither
supports a new uncertainty estimator yet.

## Cheapest decisive kill test

Do not build TTA, conformal, or a new loss. If C3 is reopened, run one small
severity sweep using the existing generator and the same five seeds:

```text
shifts: density_drift, prior_shift
drift_strength: 0, .25, .5, .75, 1.0
evaluate: every t=0..9 batch
methods: GBC kmeans/class_means tau=.85 and validation-selected tau
baselines: RF, calibrated RF, RBF-SVM, 5-NN
store: Accuracy, ECE, Brier, NLL, confidence ties, SelR50, AUROC(error score)
```

Freeze the following kill rule before running: **permanently reject the shift/UQ
line unless, in both shifts and at least 4/5 seeds, GBC ECE is at least 5 pp or
Brier is at least 2 pp worse than the calibrated reference at least one severity
step before Accuracy loses 1 pp, while calibrated baselines do not show the same
ordering.**
Also kill if max-probability ties exceed 50% and a distance/density-aware score
does not improve error-detection AUROC by at least .05 without labels from the
target batch.

This is the cheapest valid test because it reuses all code and adds only 100
small runs, while supplying the missing temporal/severity axis and a calibrated
control. The current 40-run endpoint batch is sufficient to reject C3 now; no
larger dataset is justified before this test passes.
"""


def main() -> None:
    records = load_records()
    report = render_report(records)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "records": len(records),
                "constant_confidence_records": sum(
                    is_provably_constant_confidence(record) for record in records
                ),
                "decision": "REJECT",
                "report": str(REPORT.relative_to(ROOT)),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
