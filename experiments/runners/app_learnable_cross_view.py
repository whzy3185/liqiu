"""Runner for learnable anisotropic granular-ball cross-view recovery."""

from typing import Any, Mapping

from studies.application_learnable import evaluate_learnable_cross_view


def run(config: Mapping[str, Any]):
    result = evaluate_learnable_cross_view(
        config["dataset_generation_parameters"]["dataset"],
        int(config["seed"]),
        int(config["hyperparameters"]["epochs"]),
    )
    primary = next(
        row for row in result["frontier"] if row["method"] == "anisotropic_gb" and row["missing_rate"] == 0.40
    )
    references = [
        row for row in result["frontier"] if row["method"] != "anisotropic_gb" and row["missing_rate"] == 0.40
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
            "granule_count": result["regions"],
            "average_granule_size": None,
            "uncertain_sample_ratio": 0.40,
            "additional": {
                "application_role": "learnable anisotropic cross-view region",
                "device": result["device"],
            },
        },
        "outcome": "success",
        "notes": "GB application test: learnable anisotropic region module for missing-view recovery.",
    }
