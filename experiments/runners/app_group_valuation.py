"""Runner for granular-ball grouped data valuation tests."""

from typing import Any, Mapping

from studies.application_valuation import evaluate_group_influence


def run(config: Mapping[str, Any]):
    result = evaluate_group_influence(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    candidate = next(row for row in result["methods"] if row["method"] == "granular_ball")
    references = [row for row in result["methods"] if row["method"] != "granular_ball"]
    best_correlation = max(references, key=lambda row: row["spearman_exact_influence"])
    best_noise = max(references, key=lambda row: row["noise_auprc"])
    return {
        "metrics": {
            "accuracy": candidate["spearman_exact_influence"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_correlation_reference": best_correlation["method"],
                "best_noise_reference": best_noise["method"],
                "correlation_gap_vs_best": candidate["spearman_exact_influence"]
                - best_correlation["spearman_exact_influence"],
                "noise_auprc_gap_vs_best": candidate["noise_auprc"] - best_noise["noise_auprc"],
                "retrain_reduction_vs_exact": 1 - candidate["retrains"] / result["exact_retrains"],
            },
        },
        "structure": {
            "granule_count": candidate["groups"],
            "average_granule_size": result["train_items"] / candidate["groups"],
            "uncertain_sample_ratio": result["noise_rate"],
            "additional": {"application_role": "grouped training-data valuation unit"},
        },
        "outcome": "success",
        "notes": "GB application test: grouped leave-out approximation to exact data influence.",
    }
