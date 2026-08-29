"""Report decision-rule attribution on frozen structural-stability scenarios."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau


INPUT = Path("results/structural_stability_component_attribution.csv")
REPORT = Path("reports/structural_stability_component_attribution.md")
SUMMARY = Path("artifacts/structural_stability_component_attribution_summary.json")
BASE = "nearest_center"


def table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(f"{value:.4f}" if isinstance(value, float) else str(value) for value in row) + " |")
    return "\n".join(lines)


def rank_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["dataset", "perturbation_type", "perturbation_strength", "seed"]
    for condition, group in frame.groupby(keys):
        scores = {name: value.set_index("generator").prediction_agreement for name, value in group.groupby("decision_rule")}
        baseline = scores[BASE]
        for decision, current in scores.items():
            common = baseline.index.intersection(current.index)
            tau = kendalltau(baseline.loc[common].rank(ascending=False), current.loc[common].rank(ascending=False)).statistic
            total = reversals = 0
            for left, right in itertools.combinations(common, 2):
                base_sign = np.sign(baseline[left] - baseline[right])
                current_sign = np.sign(current[left] - current[right])
                if base_sign and current_sign:
                    total += 1
                    reversals += int(base_sign != current_sign)
            rows.append({"decision_rule": decision, "kendall_tau_vs_nearest": float(tau), "pairwise_rank_reversal_rate": reversals / total if total else float("nan"), "best_generator_retained": int(baseline.idxmax() == current.idxmax()), "condition": "|".join(map(str, condition))})
    return pd.DataFrame(rows)


def main() -> None:
    frame = pd.read_csv(INPUT)
    decision_means = frame.groupby("decision_rule")[["prediction_agreement", "accuracy_original", "accuracy_perturbed", "decision_accuracy_gain_original_vs_nearest", "decision_accuracy_gain_perturbed_vs_nearest"]].mean().reset_index()
    ranks = rank_metrics(frame)
    rank_means = ranks.groupby("decision_rule")[["kendall_tau_vs_nearest", "pairwise_rank_reversal_rate", "best_generator_retained"]].mean().reset_index()
    native = frame[frame.decision_rule == "native_radius_aware"]
    radius = frame[frame.decision_rule == "radius_aware_distance"]
    order = ["dataset", "generator", "seed"]
    native_equals_radius = native.sort_values(order).prediction_agreement.to_numpy().tolist() == radius.sort_values(order).prediction_agreement.to_numpy().tolist()
    payload = {"protocol": "structural_stability_component_attribution_v1", "rows": len(frame), "scenario_count": frame[["dataset", "perturbation_type", "perturbation_strength"]].drop_duplicates().shape[0], "decision_means": json.loads(decision_means.round(6).to_json(orient="records")), "rank_means": json.loads(rank_means.round(6).to_json(orient="records")), "native_equals_radius_aware": native_equals_radius, "status": "STRUCTURAL_STABILITY_COMPONENT_SENSITIVE"}
    SUMMARY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    three = rank_means.loc[rank_means.decision_rule == "three_center_inverse_distance_vote"].iloc[0]
    radius_row = rank_means.loc[rank_means.decision_rule == "radius_aware_distance"].iloc[0]
    report = "\n".join([
        "# Structural Stability Component Attribution v1", "",
        "This frozen follow-up holds each original/perturbed granular representation fixed and changes only the prediction rule. It contains %d rows: four pre-frozen scenarios, five complete perturbation seeds, four repository implementations, and four decision rules. No new dataset, severity, generator, or seed was added after the cheap-test outcome." % len(frame), "",
        "## Decision-level means", "", table(decision_means.round(4)), "",
        "`native_radius_aware` is exactly equal to `radius_aware_distance` for these v1 repository implementations: **%s**. This equality is an implementation fact, not evidence that paper-native rules are universally equivalent." % ("YES" if native_equals_radius else "NO"), "",
        "## Generator-ranking sensitivity", "",
        "Each row below compares the generator ranking by prediction agreement under a decision with the ranking under nearest-center for the same dataset, perturbation and seed. Pairwise reversals exclude tied comparisons.", "", table(rank_means.round(4)), "",
        "The three-center vote has mean Kendall tau %.4f against nearest-center and retains the same best generator in %.0f%% of frozen conditions. Radius-aware/native prediction has substantially lower rank agreement and only %.0f%% best-generator retention." % (three.kendall_tau_vs_nearest, 100 * three.best_generator_retained, 100 * radius_row.best_generator_retained), "",
        "Decision: `STRUCTURAL_STABILITY_COMPONENT_SENSITIVE`. The representation-level decoupling remains present, but the observed predictive-stability ranking is not generator-only: changing the fixed structure's decision rule changes both agreement and rank ordering. This supports the narrow conceptual claim that structural stability, predictive stability, and decision-rule stability must be reported separately. It does not yet support a universal author-method ranking.", "",
    ])
    REPORT.write_text(report, encoding="utf-8")
    print({"status": payload["status"], "rows": len(frame)})


if __name__ == "__main__":
    main()
