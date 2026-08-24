"""Analyze the frozen local annotator competence application test."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/results/experiments.jsonl"
REPORT = ROOT / "reports/application_exploration/crowd_competence_report.md"
STUDY = "granular-ball-application-crowd-competence"
DATASETS = ("moons", "breast_cancer", "digits")
REGIMES = ("axis", "voronoi", "nonlinear", "global_control")
SEEDS = (1, 7, 21, 42, 2026)


def mean(values):
    return statistics.fmean(values)


def method_row(record, method):
    return next(row for row in record["additional_metrics"]["methods"] if row["method"] == method)


def load():
    records = [
        json.loads(line)
        for line in RESULTS.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records = [record for record in records if record.get("study") == STUDY]
    if len(records) != 60 or any(record.get("outcome") != "success" for record in records):
        raise ValueError(f"expected 60 successful records, got {len(records)}")
    observed = {
        (
            record["dataset_generation_parameters"]["dataset"],
            record["dataset_generation_parameters"]["regime"],
            int(record["seed"]),
        )
        for record in records
    }
    expected = {
        (dataset, regime, seed)
        for dataset in DATASETS
        for regime in REGIMES
        for seed in SEEDS
    }
    if observed != expected or len({record["experiment_id"] for record in records}) != 60:
        raise ValueError("crowd-competence grid mismatch")
    return records


def main():
    records = load()
    cells = {}
    for regime in REGIMES:
        for dataset in DATASETS:
            subset = [
                record
                for record in records
                if record["dataset_generation_parameters"]
                == {"dataset": dataset, "regime": regime}
            ]
            candidate = [method_row(record, "gb_surface_multiscale") for record in subset]
            center = [method_row(record, "gb_center_multiscale") for record in subset]
            ds = [method_row(record, "dawid_skene") for record in subset]
            oracle = [method_row(record, "oracle_local") for record in subset]
            cells[dataset, regime] = {
                "aggregation": mean(row["aggregation_accuracy"] for row in candidate),
                "ds_aggregation": mean(row["aggregation_accuracy"] for row in ds),
                "oracle_aggregation": mean(row["aggregation_accuracy"] for row in oracle),
                "competence": mean(row["competence_auprc"] for row in candidate),
                "competence_gap_best": mean(
                    record["additional_metrics"]["competence_auprc_gap_vs_best"]
                    for record in subset
                ),
                "competence_gap_center": mean(
                    first["competence_auprc"] - second["competence_auprc"]
                    for first, second in zip(candidate, center)
                ),
                "allocation": mean(row["allocation_accuracy_auc"] for row in candidate),
                "allocation_gap_best": mean(
                    record["additional_metrics"]["allocation_auc_gap_vs_best"]
                    for record in subset
                ),
                "allocation_gap_center": mean(
                    first["allocation_accuracy_auc"] - second["allocation_accuracy_auc"]
                    for first, second in zip(candidate, center)
                ),
                "runtime": mean(row["runtime_seconds"] for row in candidate),
            }

    region_records = [
        record
        for record in records
        if record["dataset_generation_parameters"]["regime"] != "global_control"
    ]
    gates = {
        "competence_vs_best": sum(
            record["additional_metrics"]["competence_auprc_gap_vs_best"] >= 0.03
            for record in region_records
        ),
        "allocation_vs_best": sum(
            record["additional_metrics"]["allocation_auc_gap_vs_best"] >= 0.01
            for record in region_records
        ),
        "competence_attribution": sum(
            record["additional_metrics"]["competence_gap_vs_center_ablation"] >= 0.02
            for record in region_records
        ),
        "allocation_attribution": sum(
            record["additional_metrics"]["allocation_gap_vs_center_ablation"] >= 0.005
            for record in region_records
        ),
    }
    mean_gaps = {
        "competence_best": mean(
            record["additional_metrics"]["competence_auprc_gap_vs_best"]
            for record in region_records
        ),
        "allocation_best": mean(
            record["additional_metrics"]["allocation_auc_gap_vs_best"]
            for record in region_records
        ),
        "competence_center": mean(
            record["additional_metrics"]["competence_gap_vs_center_ablation"]
            for record in region_records
        ),
        "allocation_center": mean(
            record["additional_metrics"]["allocation_gap_vs_center_ablation"]
            for record in region_records
        ),
    }
    table = "\n".join(
        f"| {dataset} | {regime} | {cells[dataset, regime]['aggregation']:.3f} | "
        f"{cells[dataset, regime]['ds_aggregation']:.3f} | "
        f"{cells[dataset, regime]['oracle_aggregation']:.3f} | "
        f"{cells[dataset, regime]['competence']:.3f} | "
        f"{cells[dataset, regime]['competence_gap_best']:+.3f} | "
        f"{cells[dataset, regime]['competence_gap_center']:+.3f} | "
        f"{cells[dataset, regime]['allocation_gap_best']:+.3f} | "
        f"{cells[dataset, regime]['allocation_gap_center']:+.3f} |"
        for regime in REGIMES
        for dataset in DATASETS
    )
    report = f"""# GB application: local annotator competence

Generated by `python scripts/analyze_app_crowd_competence.py` from the
append-only ledger. Audit date: 2026-08-25.

## Decision

**`REJECT` the tested granular-ball mechanism.** Local annotator competence is a
real exploitable problem in the simulator, but full radius-aware multiscale GB
does not beat strong local competence models and has no same-partition radius
attribution.

Across the 45 region-dependent runs, GB trails the best non-oracle competence
baseline by {abs(mean_gaps['competence_best']):.3f} AUPRC and the best allocation
baseline by {abs(mean_gaps['allocation_best']):.3f} Accuracy-cost AUC on average.
It clears the +.03 competence gate in {gates['competence_vs_best']}/45 and the
+.01 allocation gate in {gates['allocation_vs_best']}/45. Against the identical
center-only multiscale partition, mean gaps are
{mean_gaps['competence_center']:+.4f} competence AUPRC and
{mean_gaps['allocation_center']:+.4f} allocation AUC.

## Frozen protocol

- Three semi-real datasets (`moons`, Breast Cancer, Digits), three hidden local
  competence geometries and five seeds, plus 15 global-only negative controls:
  60 successful CPU runs.
- Sixteen annotators include global-good/global-bad, region/class specialists,
  boundary-poor and local-adversarial types. Region-dependent workers are
  calibrated near the same mean quality so local heterogeneity is not a hidden
  global-quality advantage.
- Hidden regions are axis boxes, KMeans/Voronoi cells or nonlinear random-feature
  cells. They are simulator-only and never derived from evaluated GB partitions.
- Truth is visible only to the simulator and final metrics. Methods fit global
  Dawid-Skene on competence items, estimate local competence from soft pseudo-
  truth, and aggregate a separate allocation pool.
- Two initial labels per allocation item; extra labels are pre-realized once,
  capacity-limited per worker and never resampled. One unqueryable worker-item
  probe per item evaluates competence without queried-only selection bias.

| Dataset | Regime | GB agg | DS agg | Oracle-local agg | GB competence AUPRC | Gap best competence | Gap center | Gap best allocation | Gap center allocation |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
{table}

## What is real in the result

Oracle-local aggregation exceeds global DS in most region-dependent cells,
often by several percentage points. For example, Breast Cancer/Voronoi reaches
{cells['breast_cancer', 'voronoi']['oracle_aggregation']:.3f} with true local
competence versus {cells['breast_cancer', 'voronoi']['ds_aggregation']:.3f} for
DS. The application pain point is therefore not fabricated.

The tested estimator fails to recover that opportunity. kNN, tree, terminal GB
or matched KMeans is the strongest competence reference depending on the cell;
kNN is most frequently strongest for allocation. Multiscale surface routing is
never the consistent winner.

## Attribution and controls

- Competence gate versus the strongest baseline: {gates['competence_vs_best']}/45.
- Allocation gate versus the strongest baseline: {gates['allocation_vs_best']}/45.
- +.02 competence attribution versus same-tree center-only: {gates['competence_attribution']}/45.
- +.005 allocation attribution versus same-tree center-only:
  {gates['allocation_attribution']}/45, without the required competence gate.
- Global-only controls show no meaningful reason to introduce local regions;
  the oracle-local and DS aggregation means are already nearly identical.

## Limitations

- Breast Cancer and Digits provide real item geometry and truth, but annotators
  are simulated; Moons is fully synthetic. These are semi-real mechanism tests,
  not a real crowdsourcing benchmark claim.
- The local model uses scalar correctness with symmetric off-diagonal errors,
  not full local confusion matrices or iterative local DS EM.
- Allocation uses a fixed expected-information proxy and equal worker capacity;
  cost-aware experts and online competence updates were deliberately deferred.
- NUTMEG/GLAD/MACE were not runnable in the environment. Strong global DS and
  matched local kNN/KMeans/tree controls are present, but this is not a full
  crowdsourcing benchmark.

The missing full local-confusion mechanism cannot rescue failed radius
attribution: center-only sees the same pseudo-truth, hierarchy and shrinkage and
performs the same or better. Do not tune radius, kappa, split gain or region
count, and do not expand to real crowd data for this mechanism.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "records": len(records),
                "decision": "REJECT",
                "gates": gates,
                "mean_gaps": mean_gaps,
                "report": str(REPORT.relative_to(ROOT)),
            }
        )
    )


if __name__ == "__main__":
    main()
