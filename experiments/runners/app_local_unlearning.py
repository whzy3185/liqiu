"""Runner for fixed-region granular-ball approximate unlearning."""

from typing import Any, Mapping

from studies.application_unlearning import evaluate_local_unlearning


def run(config: Mapping[str, Any]):
    result = evaluate_local_unlearning(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    primary = next(
        row
        for row in result["frontier"]
        if row["method"] == "granular_ball" and row["scenario"] == "local_concentrated"
    )
    references = [
        row
        for row in result["frontier"]
        if row["method"] != "granular_ball" and row["scenario"] == "local_concentrated"
    ]
    best_agreement = max(references, key=lambda row: row["agreement_with_full_retrain"])
    return {
        "metrics": {
            "accuracy": primary["agreement_with_full_retrain"],
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "best_agreement_reference": best_agreement["method"],
                "agreement_gap_vs_best": primary["agreement_with_full_retrain"]
                - best_agreement["agreement_with_full_retrain"],
                "speedup_gap_vs_best": primary["speedup"] - max(row["speedup"] for row in references),
            },
        },
        "structure": {
            "granule_count": primary["updated_groups"],
            "average_granule_size": result["train_items"] / primary["updated_groups"],
            "uncertain_sample_ratio": primary["deletion_fraction"],
            "additional": {"application_role": "localized deletion update region"},
        },
        "outcome": "success",
        "notes": "GB application test: approximate local deletion, not certified unlearning.",
    }
