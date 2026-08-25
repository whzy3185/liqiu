"""Runner for granular-ball spatial sensor placement tests."""

from typing import Any, Mapping

from studies.application_sensor import evaluate_sensor_placement


def run(config: Mapping[str, Any]):
    result = evaluate_sensor_placement(
        config["dataset_generation_parameters"]["family"], int(config["seed"])
    )
    primary = next(
        row
        for row in result["frontier"]
        if row["method"] == "granular_ball" and row["fraction"] == 0.10
    )
    references = [
        row
        for row in result["frontier"]
        if row["method"] != "granular_ball" and row["fraction"] == 0.10
    ]
    best_rmse = min(references, key=lambda row: row["normalized_rmse"])
    best_worst = min(references, key=lambda row: row["worst_region_rmse"])
    return {
        "metrics": {
            "accuracy": 1 - primary["normalized_rmse"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_rmse_reference": best_rmse["method"],
                "best_worst_region_reference": best_worst["method"],
                "relative_rmse_gain_vs_best": (
                    best_rmse["normalized_rmse"] - primary["normalized_rmse"]
                )
                / best_rmse["normalized_rmse"],
                "relative_worst_region_gain_vs_best": (
                    best_worst["worst_region_rmse"] - primary["worst_region_rmse"]
                )
                / best_worst["worst_region_rmse"],
            },
        },
        "structure": {
            "granule_count": primary["sensors"],
            "average_granule_size": result["sites"] / primary["sensors"],
            "uncertain_sample_ratio": None,
            "additional": {"application_role": "sensor-budget spatial region"},
        },
        "outcome": "success",
        "notes": "GB application test: fixed-budget spatial monitoring-network thinning.",
    }
