"""Runner for matched granular-ball batch active-learning tests."""

from typing import Any, Mapping

from studies.application_active import evaluate_batch_active_learning


def run(config: Mapping[str, Any]):
    result = evaluate_batch_active_learning(
        config["dataset_generation_parameters"]["dataset"], int(config["seed"])
    )
    candidate = next(row for row in result["methods"] if row["method"] == "gb_radius_batch")
    references = [row for row in result["methods"] if row is not candidate]
    best_reference = max(references, key=lambda row: row["accuracy_auc"])
    ablation = next(row for row in references if row["method"] == "gb_center_batch")
    return {
        "metrics": {
            "accuracy": candidate["curve"][-1]["accuracy"],
            "macro_f1": candidate["curve"][-1]["macro_f1"],
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "candidate_accuracy_auc": candidate["accuracy_auc"],
                "best_reference_method": best_reference["method"],
                "accuracy_auc_gap_vs_best_reference": candidate["accuracy_auc"]
                - best_reference["accuracy_auc"],
                "accuracy_auc_gap_vs_center_ablation": candidate["accuracy_auc"]
                - ablation["accuracy_auc"],
            },
        },
        "structure": {
            "granule_count": None,
            "average_granule_size": None,
            "uncertain_sample_ratio": None,
            "additional": {"application_role": "batch annotation unit"},
        },
        "outcome": "success",
        "notes": "GB application test: matched pool-based batch active learning.",
    }
