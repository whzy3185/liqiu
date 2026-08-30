"""Summarize the frozen real-data fresh-routing purity audit without tuning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def weighted(group, column):
    group = group.dropna(subset=[column, "fresh_weight"])
    return float(np.average(group[column], weights=group["fresh_weight"])) if len(group) else np.nan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = pd.read_csv(args.input_dir / "ball_level.csv")
    selective = pd.read_csv(args.input_dir / "selective.csv")

    method_rows = []
    for (dataset, seed, method), group in rows.groupby(["dataset", "seed", "method"]):
        valid = group.dropna(subset=["fresh_correctness"])
        high_small = valid[(valid["train_purity"] >= 0.9) & (valid["support_structure"] <= 5)]
        method_rows.append({
            "dataset": dataset,
            "seed": int(seed),
            "method": method,
            "weighted_train_optimism": weighted(valid, "optimism_train"),
            "weighted_calibration_error": weighted(valid, "optimism_cal"),
            "high_purity_small_gap": weighted(high_small, "optimism_train"),
            "high_purity_small_mass": float(high_small["fresh_weight"].sum()),
            "native_construction_overlap": float(valid["construction_native_overlap"].dropna().median()) if valid["construction_native_overlap"].notna().any() else np.nan,
            "mean_structure_support": float(valid["support_structure"].mean()),
            "min_structure_support": int(valid["support_structure"].min()),
            "ball_count": int(len(valid)),
        })
    method = pd.DataFrame(method_rows)
    method.to_csv(args.output_dir / "method_seed_summary.csv", index=False)

    comparison = []
    for (dataset, seed), group in method.groupby(["dataset", "seed"]):
        adaptive = group[group.method == "gb_adaptive_parameter_free"]
        cart = group[group.method == "cart_matched_adaptive_leaf_count"]
        if len(adaptive) and len(cart):
            comparison.append({
                "dataset": dataset, "seed": int(seed),
                "adaptive_minus_cart_optimism": float(adaptive.iloc[0].weighted_train_optimism - cart.iloc[0].weighted_train_optimism),
                "adaptive_overlap": float(adaptive.iloc[0].native_construction_overlap),
                "adaptive_high_small_gap": float(adaptive.iloc[0].high_purity_small_gap),
                "adaptive_high_small_mass": float(adaptive.iloc[0].high_purity_small_mass),
            })
    comparison = pd.DataFrame(comparison)
    comparison.to_csv(args.output_dir / "adaptive_vs_cart.csv", index=False)

    selective_summary = selective.groupby(["dataset", "seed", "method", "target_coverage"]).apply(
        lambda g: pd.Series({
            "risk_train": g.loc[g.score == "train_purity", "test_risk"].iloc[0],
            "risk_cal": g.loc[g.score == "cal_purity", "test_risk"].iloc[0],
            "risk_laplace": g.loc[g.score == "laplace_purity", "test_risk"].iloc[0],
            "risk_wilson": g.loc[g.score == "wilson_lower", "test_risk"].iloc[0],
            "coverage_train": g.loc[g.score == "train_purity", "test_coverage"].iloc[0],
            "coverage_cal": g.loc[g.score == "cal_purity", "test_coverage"].iloc[0],
        }), include_groups=False
    ).reset_index()
    selective_summary["cal_minus_train_risk"] = selective_summary.risk_cal - selective_summary.risk_train
    selective_summary["laplace_minus_train_risk"] = selective_summary.risk_laplace - selective_summary.risk_train
    selective_summary["wilson_minus_train_risk"] = selective_summary.risk_wilson - selective_summary.risk_train
    selective_summary.to_csv(args.output_dir / "selective_summary.csv", index=False)

    adaptive = method[method.method == "gb_adaptive_parameter_free"]
    per_dataset = []
    for dataset, group in adaptive.groupby("dataset"):
        paired = comparison[comparison.dataset == dataset]
        per_dataset.append({
            "dataset": dataset,
            "adaptive_weighted_optimism_median": float(group.weighted_train_optimism.median()),
            "adaptive_positive_all_seeds": bool((group.weighted_train_optimism > 0).all()),
            "adaptive_high_purity_small_gap_median": float(group.high_purity_small_gap.dropna().median()) if group.high_purity_small_gap.notna().any() else np.nan,
            "adaptive_high_purity_small_mass_median": float(group.high_purity_small_mass.median()),
            "adaptive_minus_cart_median": float(paired.adaptive_minus_cart_optimism.median()) if len(paired) else np.nan,
            "adaptive_exceeds_cart_all_seeds_by_2pp": bool((paired.adaptive_minus_cart_optimism >= .02).all()) if len(paired) else False,
            "native_construction_overlap_median": float(group.native_construction_overlap.median()),
        })
    per_dataset = pd.DataFrame(per_dataset)
    per_dataset.to_csv(args.output_dir / "dataset_gate_summary.csv", index=False)

    go = {
        "positive_adaptive_optimism_datasets": int(per_dataset.adaptive_positive_all_seeds.sum()),
        "high_purity_small_gap_ge_5pp_datasets": int((per_dataset.adaptive_high_purity_small_gap_median >= .05).sum()),
        "adaptive_exceeds_cart_by_2pp_datasets": int(per_dataset.adaptive_exceeds_cart_all_seeds_by_2pp.sum()),
        "all_real_datasets": int(len(per_dataset)),
        "go_conditions_met": bool(
            (per_dataset.adaptive_positive_all_seeds.sum() >= 4)
            and ((per_dataset.adaptive_high_purity_small_gap_median >= .05).sum() >= 4)
            and (per_dataset.adaptive_exceeds_cart_all_seeds_by_2pp.sum() >= 4)
        ),
    }
    go["verdict"] = "GO_TO_CORRECTION_CONFIRMATION" if go["go_conditions_met"] else "KILL_OR_DOWNGRADE_GB_SPECIFIC_CLAIM"
    (args.output_dir / "gate_decision.json").write_text(json.dumps(go, indent=2), encoding="utf-8")
    print(json.dumps(go, indent=2))


if __name__ == "__main__":
    main()
