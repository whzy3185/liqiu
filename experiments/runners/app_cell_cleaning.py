"""Runner for the contextual granular-ball cell-cleaning application test."""

from typing import Any, Mapping

from studies.application_cleaning import evaluate_cell_cleaning


def run(config: Mapping[str, Any]):
    result = evaluate_cell_cleaning(
        config["dataset_generation_parameters"]["dataset"],
        int(config["seed"]),
        float(config["hyperparameters"]["corruption_rate"]),
        int(config["hyperparameters"]["crossfit_folds"]),
    )
    candidate = next(
        row for row in result["methods"] if row["method"] == "gb_surface_multiscale"
    )
    references = [row for row in result["methods"] if row is not candidate]
    best_reference = max(references, key=lambda row: row["cell_auprc"])
    ablation = next(
        row for row in references if row["method"] == "gb_center_multiscale"
    )
    return {
        "metrics": {
            "accuracy": candidate["downstream"]["primary"],
            "macro_f1": candidate["downstream"].get("macro_f1"),
            "auroc": None,
            "calibration_error": None,
            "additional": {
                **result,
                "candidate_cell_auprc": candidate["cell_auprc"],
                "best_reference_method": best_reference["method"],
                "cell_auprc_gap_vs_best_reference": candidate["cell_auprc"]
                - best_reference["cell_auprc"],
                "cell_auprc_gap_vs_center_ablation": candidate["cell_auprc"]
                - ablation["cell_auprc"],
            },
        },
        "structure": {
            "granule_count": result["mean_terminal_count"],
            "average_granule_size": None,
            "uncertain_sample_ratio": result["corruption_rate"],
            "additional": {
                "application_role": "cross-fitted multiscale cell context",
                "corrupted_cells": result["corrupted_cells"],
            },
        },
        "outcome": "success",
        "notes": "GB application test: contextual numeric cell detection and top-budget repair.",
    }
