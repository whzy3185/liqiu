"""Runner for granular-ball k-anonymous microaggregation tests."""

from typing import Any, Mapping

from studies.application_privacy import evaluate_microaggregation


def run(config: Mapping[str, Any]):
    result = evaluate_microaggregation(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    primary = next(
        row for row in result["frontier"] if row["method"] == "granular_ball" and row["k"] == 10
    )
    references = [
        row for row in result["frontier"] if row["method"] != "granular_ball" and row["k"] == 10
    ]
    best_distortion = min(references, key=lambda row: row["distortion_mse"])
    best_accuracy = max(references, key=lambda row: row["downstream_accuracy"])
    return {
        "metrics": {
            "accuracy": primary["downstream_accuracy"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_distortion_reference": best_distortion["method"],
                "best_accuracy_reference": best_accuracy["method"],
                "relative_distortion_gain_vs_best": (
                    best_distortion["distortion_mse"] - primary["distortion_mse"]
                )
                / best_distortion["distortion_mse"],
                "accuracy_gap_vs_best": primary["downstream_accuracy"]
                - best_accuracy["downstream_accuracy"],
            },
        },
        "structure": {
            "granule_count": primary["groups"],
            "average_granule_size": result["train_items"] / primary["groups"],
            "uncertain_sample_ratio": None,
            "additional": {
                "application_role": "k-anonymous microaggregation cell",
                "minimum_group_size": primary["minimum_group_size"],
            },
        },
        "outcome": "success",
        "notes": "GB application test: privacy microaggregation under equal k-anonymity.",
    }
