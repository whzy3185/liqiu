"""Runner for granular-ball model failure-slice discovery."""

from typing import Any, Mapping

from studies.application_slices import evaluate_failure_slices


def run(config: Mapping[str, Any]):
    result = evaluate_failure_slices(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    candidate = next(row for row in result["frontier"] if row["method"] == "granular_ball")
    references = [row for row in result["frontier"] if row["method"] != "granular_ball"]
    best_uplift = max(references, key=lambda row: row["risk_uplift"])
    best_recall = max(references, key=lambda row: row["error_recall"])
    return {
        "metrics": {
            "accuracy": candidate["risk_uplift"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_uplift_reference": best_uplift["method"],
                "best_recall_reference": best_recall["method"],
                "risk_uplift_gap_vs_best": candidate["risk_uplift"] - best_uplift["risk_uplift"],
                "error_recall_gap_vs_best": candidate["error_recall"] - best_recall["error_recall"],
            },
        },
        "structure": {
            "granule_count": candidate["regions"],
            "average_granule_size": None,
            "uncertain_sample_ratio": candidate["coverage"],
            "additional": {"application_role": "model-risk audit slice"},
        },
        "outcome": "success",
        "notes": "GB application test: validation-discovered model failure slices.",
    }
