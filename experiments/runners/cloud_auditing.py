"""Cheap Test C: fixed-budget cloud block audit sampling simulation."""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from cloud_auditing.simulation import (
    audit_policies,
    corruption_indices,
    evaluate_policy,
    generate_blocks,
)


SCENARIOS = ("uniform", "clustered", "hot_targeted", "cold_targeted", "adversarial")


def run(config: Mapping[str, Any]) -> dict:
    seed = int(config["seed"])
    sizes = config["dataset_generation_parameters"].get("sizes", [10_000, 100_000])
    rows = []
    group_counts = []
    for n in sizes:
        blocks = generate_blocks(int(n), seed + int(n))
        policies, group_count = audit_policies(blocks, seed + int(n))
        group_counts.append(group_count)
        budgets = [50, 100, 250] if int(n) == 10_000 else [100, 500, 1000]
        n_corrupt = max(20, int(round(0.01 * int(n))))
        fixed_corruption = {
            scenario: corruption_indices(blocks, scenario, n_corrupt, seed + index * 101)
            for index, scenario in enumerate(SCENARIOS[:-1])
        }
        for scenario in SCENARIOS:
            for method, policy in policies.items():
                corrupted = (
                    corruption_indices(blocks, scenario, n_corrupt, seed + 991, policy)
                    if scenario == "adversarial"
                    else fixed_corruption[scenario]
                )
                for budget in budgets:
                    metrics = evaluate_policy(
                        policy,
                        corrupted,
                        budget,
                        seed + budget + len(method) * 17,
                        repeats=int(config["hyperparameters"].get("repeats", 30)),
                    )
                    rows.append(
                        {
                            "n_blocks": int(n),
                            "scenario": scenario,
                            "method": method,
                            "budget": budget,
                            "n_corrupt": n_corrupt,
                            "n_groups": group_count if method in {
                                "kmeans_group", "tree_partition", "gb_center_only",
                                "granular_ball", "gb_three_way",
                            } else None,
                            "metrics": metrics,
                        }
                    )

    primary_rows = [
        row for row in rows
        if row["method"] == "gb_three_way" and row["scenario"] in {"clustered", "hot_targeted", "cold_targeted"}
    ]
    primary_detection = float(np.mean([row["metrics"]["detection_probability"] for row in primary_rows]))
    return {
        "metrics": {
            "accuracy": primary_detection,
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {"rows": rows},
        },
        "structure": {
            "granule_count": int(round(np.mean(group_counts))),
            "average_granule_size": float(np.mean([n / k for n, k in zip(sizes, group_counts)])),
            "uncertain_sample_ratio": None,
            "additional": {"group_counts": group_counts, "sizes": sizes},
        },
        "outcome": "success",
        "notes": (
            "Empirical audit-sampling simulation only; PDP/PoR proofs are treated as an existing "
            "lower layer. All methods receive the same block budget. Non-adversarial scenarios "
            "share corruption indices; the adversarial scenario attacks each policy's bottom "
            "sampling-probability region separately."
        ),
    }

