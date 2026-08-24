"""Runner for hard-budget granular-ball online state tests."""

from typing import Any, Mapping

from studies.application_online import evaluate_online_memory


def run(config: Mapping[str, Any]):
    result = evaluate_online_memory(
        config["dataset_generation_parameters"]["stream_kind"],
        int(config["seed"]),
        int(config["hyperparameters"]["max_balls"]),
    )
    candidate = result["methods"]["gb_surface"]
    center = result["methods"]["center_ablation"]
    sliding = result["methods"]["sliding_gbc"]
    sgd = result["methods"]["sgd"]
    best_accuracy = max(sliding["accuracy"], sgd["accuracy"])
    return {
        "metrics": {
            "accuracy": candidate["accuracy"],
            "macro_f1": candidate["macro_f1"],
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "accuracy_gap_vs_best_reference": candidate["accuracy"] - best_accuracy,
                "accuracy_gap_vs_center_ablation": candidate["accuracy"] - center["accuracy"],
                "update_time_ratio_vs_sliding": candidate["mean_update_seconds"]
                / max(sliding["mean_update_seconds"], 1e-12),
            },
        },
        "structure": {
            "granule_count": result["mean_balls"],
            "average_granule_size": None,
            "uncertain_sample_ratio": None,
            "additional": {
                "max_balls": result["max_balls"],
                "mean_memory_bytes": result["mean_memory_bytes"],
                "max_memory_bytes": result["max_memory_bytes"],
                "application_role": "hard-budget online state",
            },
        },
        "outcome": "success",
        "notes": "GB application test: local online state under a fixed ball cap.",
    }
