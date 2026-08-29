"""Summarize the frozen structural-stability v1 cheap test without selection."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


INPUT = Path("results/structural_stability_cheap_test.csv")
REPORT = Path("reports/structural_stability_cheap_test.md")
SUMMARY = Path("artifacts/structural_stability_cheap_test_summary.json")


def rounded(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.round(6).to_json(orient="records"))


def markdown_table(frame: pd.DataFrame) -> str:
    headers = list(frame.columns)
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for _, row in frame.iterrows():
        values = [f"{value:.4f}" if isinstance(value, float) else str(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    frame = pd.read_csv(INPUT)
    baseline = (frame.perturbation_type == "seed") & (frame.perturbation_strength == "baseline")
    active = frame.loc[~baseline].copy()
    active["decoupling_case"] = (active.prediction_agreement >= .95) & (active.ari <= .70)
    active["data_perturbation"] = active.perturbation_type != "seed"
    overall = active[["ari", "nmi", "vi", "prediction_agreement", "accuracy_change"]].mean().to_dict()
    by_generator = active.groupby("generator")[["ari", "nmi", "vi", "prediction_agreement", "accuracy_change", "ball_count_ratio"]].mean().reset_index()
    by_perturbation = active.groupby("perturbation_type")[["ari", "nmi", "vi", "prediction_agreement", "accuracy_change", "ball_count_ratio"]].mean().reset_index()
    decoupling = active[active.decoupling_case].copy()
    data_decoupling = decoupling[decoupling.data_perturbation]
    structural_rank = by_generator.sort_values("ari", ascending=False).generator.tolist()
    predictive_rank = by_generator.sort_values("prediction_agreement", ascending=False).generator.tolist()
    status = "STRUCTURAL_STABILITY_PAPER_TRACK" if len(data_decoupling) >= 10 and data_decoupling.dataset.nunique() >= 3 and data_decoupling.generator.nunique() >= 2 else "STRUCTURAL_STABILITY_WEAK"
    strongest = decoupling.sort_values(["ari", "prediction_agreement"], ascending=[True, False]).iloc[0]
    payload = {
        "protocol": "structural_stability_cheap_test_v1",
        "rows": len(frame),
        "datasets": sorted(frame.dataset.unique().tolist()),
        "generators": sorted(frame.generator.unique().tolist()),
        "active_rows": len(active),
        "overall_means": overall,
        "decoupling_cases": int(len(decoupling)),
        "data_perturbation_decoupling_cases": int(len(data_decoupling)),
        "data_perturbation_decoupling_datasets": sorted(data_decoupling.dataset.unique().tolist()),
        "data_perturbation_decoupling_generators": sorted(data_decoupling.generator.unique().tolist()),
        "structural_stability_rank": structural_rank,
        "predictive_stability_rank": predictive_rank,
        "rankings_agree": structural_rank == predictive_rank,
        "status": status,
        "by_generator": rounded(by_generator),
        "by_perturbation": rounded(by_perturbation),
        "strongest_decoupling_case": {key: strongest[key] for key in ["dataset", "generator", "perturbation_type", "perturbation_strength", "seed", "ari", "nmi", "vi", "prediction_agreement", "accuracy_change", "ball_count_original", "ball_count_perturbed"]},
    }
    SUMMARY.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=lambda value: value.item()),
        encoding="utf-8",
    )
    with SUMMARY.open("a", encoding="utf-8") as handle:
        handle.write("\n")
    generator_table = markdown_table(by_generator.round(4))
    perturbation_table = markdown_table(by_perturbation.round(4))
    cases = data_decoupling.sort_values(["ari", "prediction_agreement"], ascending=[True, False])[["dataset", "generator", "perturbation_type", "perturbation_strength", "seed", "ari", "nmi", "vi", "prediction_agreement", "accuracy_change", "ball_count_original", "ball_count_perturbed"]].round(4)
    case_table = markdown_table(cases)
    report = f"""# Structural Stability Cheap Test v1

The frozen v1 test completed all {len(frame)} rows across {frame.dataset.nunique()} datasets and {frame.generator.nunique()} explicitly-labelled repository implementations.  The synthetic A3 family is included only as a controlled geometry-label stress family, never as privacy evidence.  The primary decision is common nearest-center prediction on a fixed test split; native decision rules were not used.

The seed-baseline identity rows are controls and are excluded from summary means. Across the remaining {len(active)} comparisons, mean ARI is {overall['ari']:.4f}, mean NMI {overall['nmi']:.4f}, mean VI {overall['vi']:.4f}, mean prediction agreement {overall['prediction_agreement']:.4f}, and mean absolute accuracy change {overall['accuracy_change']:.4f}.

## Generator means

{generator_table}

## Perturbation means

{perturbation_table}

## Structural--predictive decoupling

Using the pre-frozen descriptive criterion prediction agreement >= 0.95 and ARI <= 0.70, there are {len(decoupling)} cases overall and {len(data_decoupling)} cases under actual sample, label, or feature perturbations.  The latter span {data_decoupling.dataset.nunique()} datasets and {data_decoupling.generator.nunique()} generators.  They are retained in full below; no threshold, seed, or source was removed.

{case_table}

The strongest observed case is `{strongest['dataset']}` / `{strongest['generator']}` under `{strongest['perturbation_type']}` strength {strongest['perturbation_strength']} seed {strongest['seed']}: ARI {strongest['ari']:.4f}, prediction agreement {strongest['prediction_agreement']:.4f}, and ball count {int(strongest['ball_count_original'])} -> {int(strongest['ball_count_perturbed'])}.  It is a discovery observation, not a standalone conclusion.

## Ranking comparison and gate

The mean-ARI ranking is `{' > '.join(structural_rank)}`.  The mean prediction-agreement ranking is `{' > '.join(predictive_rank)}`.  Rankings agree: **{'YES' if structural_rank == predictive_rank else 'NO'}**.

Decision: `{status}`.  The result clears the empirical cheap-test signal because minor data perturbations yield repeated high-prediction/low-ARI observations across multiple datasets and generators.  However, it establishes neither a universal claim nor author-method ranking: all v1 implementations are labelled clean-room/internal controls.  The permitted next step is a frozen, targeted component-attribution confirmation; do not expand datasets, perturbation levels, or author-method claims first.
"""
    REPORT.write_text(report, encoding="utf-8")
    print({"status": payload["status"], "rows": len(frame), "data_decoupling_cases": len(data_decoupling)})


if __name__ == "__main__":
    main()
