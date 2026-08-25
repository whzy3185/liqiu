"""Runner for granular-ball compressed gallery retrieval tests."""

from typing import Any, Mapping

from studies.application_retrieval import evaluate_gallery_retrieval


def run(config: Mapping[str, Any]):
    result = evaluate_gallery_retrieval(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    primary = next(
        row
        for row in result["frontier"]
        if row["method"] == "granular_ball" and row["fraction"] == 0.10
    )
    references = [
        row
        for row in result["frontier"]
        if row["method"] not in ("granular_ball", "full") and row["fraction"] == 0.10
    ]
    best_map = max(references, key=lambda row: row["map_at_10"])
    best_rare = max(references, key=lambda row: row["rare_hit_at_10"])
    return {
        "metrics": {
            "accuracy": primary["map_at_10"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_map_reference": best_map["method"],
                "best_rare_reference": best_rare["method"],
                "map_gap_vs_best": primary["map_at_10"] - best_map["map_at_10"],
                "rare_hit_gap_vs_best": primary["rare_hit_at_10"]
                - best_rare["rare_hit_at_10"],
                "distance_reduction_vs_full": 1 - primary["slots"] / result["gallery_size"],
            },
        },
        "structure": {
            "granule_count": primary["slots"],
            "average_granule_size": result["gallery_size"] / primary["slots"],
            "uncertain_sample_ratio": None,
            "additional": {"application_role": "compressed retrieval gallery"},
        },
        "outcome": "success",
        "notes": "GB application test: fixed-slot visual/spectral gallery retrieval.",
    }
