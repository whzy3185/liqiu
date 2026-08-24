"""Runner for granular-ball local annotator competence tests."""

from typing import Any, Mapping

from studies.application_crowd import evaluate_local_competence


def run(config: Mapping[str, Any]):
    params = config["dataset_generation_parameters"]
    result = evaluate_local_competence(params["dataset"], params["regime"], int(config["seed"]))
    candidate = next(
        row for row in result["methods"] if row["method"] == "gb_surface_multiscale"
    )
    non_oracle = [
        row
        for row in result["methods"]
        if row["method"] not in ("gb_surface_multiscale", "oracle_local")
    ]
    best_competence = max(non_oracle, key=lambda row: row["competence_auprc"])
    best_allocation = max(non_oracle, key=lambda row: row["allocation_accuracy_auc"])
    ablation = next(
        row for row in non_oracle if row["method"] == "gb_center_multiscale"
    )
    return {
        "metrics": {
            "accuracy": candidate["aggregation_accuracy"],
            "macro_f1": candidate["macro_f1"],
            "auroc": None,
            "calibration_error": candidate["ece"],
            "additional": {
                **result,
                "best_competence_reference": best_competence["method"],
                "best_allocation_reference": best_allocation["method"],
                "competence_auprc_gap_vs_best": candidate["competence_auprc"]
                - best_competence["competence_auprc"],
                "allocation_auc_gap_vs_best": candidate["allocation_accuracy_auc"]
                - best_allocation["allocation_accuracy_auc"],
                "competence_gap_vs_center_ablation": candidate["competence_auprc"]
                - ablation["competence_auprc"],
                "allocation_gap_vs_center_ablation": candidate["allocation_accuracy_auc"]
                - ablation["allocation_accuracy_auc"],
            },
        },
        "structure": {
            "granule_count": result["terminal_balls"],
            "average_granule_size": result["items"]["competence"] / result["terminal_balls"],
            "uncertain_sample_ratio": None,
            "additional": {"application_role": "local annotator competence region"},
        },
        "outcome": "success",
        "notes": "GB application test: local annotator competence and capacity-limited extra labels.",
    }
