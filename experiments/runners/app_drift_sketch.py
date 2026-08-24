"""Runner for granular-ball distribution-monitoring application tests."""

from typing import Any, Mapping

from studies.application_drift import evaluate_drift_sketches


def run(config: Mapping[str, Any]):
    params = config["dataset_generation_parameters"]
    hyper = config["hyperparameters"]
    rows = evaluate_drift_sketches(
        shift_kind=params["shift_kind"],
        seed=int(config["seed"]),
        dimension=int(params["dimension"]),
        reference_size=int(params["reference_size"]),
        batch_size=int(params["batch_size"]),
        budgets=tuple(int(value) for value in hyper["budgets"]),
        severities=tuple(float(value) for value in hyper["severities"]),
        calibration_batches=int(hyper["calibration_batches"]),
        repeats=int(hyper["repeats"]),
    )
    primary = next(
        row
        for row in rows
        if row["method"] == "granular_ball" and row["budget"] == 16
    )
    equal_memory = [
        row
        for row in rows
        if row["budget"] == 16 and row["method"] in ("kmeans", "reservoir_mmd")
    ]
    best_reference = max(equal_memory, key=lambda row: row["auroc"])
    full = next(row for row in rows if row["method"] == "full_mmd")
    return {
        "metrics": {
            "accuracy": primary["auroc"],
            "macro_f1": None,
            "auroc": primary["auroc"],
            "calibration_error": primary["false_positive_rate"],
            "additional": {
                "frontier": rows,
                "best_equal_memory_method": best_reference["method"],
                "auroc_gap_vs_best_equal_memory": primary["auroc"]
                - best_reference["auroc"],
                "auroc_gap_vs_full_mmd": primary["auroc"] - full["auroc"],
                "memory_reduction_vs_full_mmd": 1
                - primary["memory_bytes"] / full["memory_bytes"],
            },
        },
        "structure": {
            "granule_count": 16,
            "average_granule_size": params["reference_size"] / 16,
            "uncertain_sample_ratio": None,
            "additional": {
                "memory_bytes": primary["memory_bytes"],
                "application_role": "fixed-memory distribution sketch",
            },
        },
        "outcome": "success",
        "notes": "GB application test: edge distribution monitoring at equal sketch budget.",
    }
