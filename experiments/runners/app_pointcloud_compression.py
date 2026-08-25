"""Runner for granular-ball point-cloud compression and retrieval."""

from typing import Any, Mapping

from studies.application_pointcloud import evaluate_pointcloud_compression


def run(config: Mapping[str, Any]):
    result = evaluate_pointcloud_compression(
        config["dataset_generation_parameters"]["regime"], int(config["seed"])
    )
    primary = next(
        row
        for row in result["frontier"]
        if row["method"] == "granular_ball" and row["budget"] == 64
    )
    references = [
        row
        for row in result["frontier"]
        if row["method"] not in ("granular_ball", "full") and row["budget"] == 64
    ]
    best_map = max(references, key=lambda row: row["map_at_10"])
    best_chamfer = min(references, key=lambda row: row["mean_chamfer"])
    return {
        "metrics": {
            "accuracy": primary["map_at_10"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_map_reference": best_map["method"],
                "best_chamfer_reference": best_chamfer["method"],
                "map_gap_vs_best": primary["map_at_10"] - best_map["map_at_10"],
                "relative_chamfer_gain_vs_best": (
                    best_chamfer["mean_chamfer"] - primary["mean_chamfer"]
                )
                / best_chamfer["mean_chamfer"],
                "point_reduction_vs_full": 1 - primary["budget"] / result["points"],
            },
        },
        "structure": {
            "granule_count": primary["budget"],
            "average_granule_size": result["points"] / primary["budget"],
            "uncertain_sample_ratio": None,
            "additional": {"application_role": "point-cloud weighted compression"},
        },
        "outcome": "success",
        "notes": "GB application test: equal-point-budget shape retrieval and reconstruction.",
    }
