"""Runner for granular-ball missing-view recovery."""

from typing import Any, Mapping

from studies.application_missingview import evaluate_missing_view


def run(config: Mapping[str, Any]):
    result = evaluate_missing_view(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    primary = next(
        row for row in result["frontier"] if row["method"] == "gb_multiscale" and row["missing_rate"] == 0.40
    )
    references = [
        row for row in result["frontier"] if row["method"] != "gb_multiscale" and row["missing_rate"] == 0.40
    ]
    best_rmse = min(references, key=lambda row: row["imputation_nrmse"])
    best_accuracy = max(references, key=lambda row: row["accuracy"])
    return {
        "metrics": {
            "accuracy": primary["accuracy"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_rmse_reference": best_rmse["method"],
                "best_accuracy_reference": best_accuracy["method"],
                "relative_rmse_gain_vs_best": (
                    best_rmse["imputation_nrmse"] - primary["imputation_nrmse"]
                )
                / best_rmse["imputation_nrmse"],
                "accuracy_gap_vs_best": primary["accuracy"] - best_accuracy["accuracy"],
            },
        },
        "structure": {
            "granule_count": result["terminal_balls"],
            "average_granule_size": None,
            "uncertain_sample_ratio": 0.40,
            "additional": {"application_role": "cross-view local recovery region"},
        },
        "outcome": "success",
        "notes": "GB application test: inference-time missing-view recovery.",
    }
