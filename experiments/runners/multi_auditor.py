"""Cheap Test D: malicious and unreliable multi-auditor aggregation."""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from multi_auditor.simulation import evaluate_methods, generate_world


def run(config: Mapping[str, Any]) -> dict:
    seed = int(config["seed"])
    rows = []
    ordinal = 0
    for n_auditors in (20, 50, 100):
        for malicious_ratio in (0.1, 0.3):
            for collusion_strength in (0.5, 1.0):
                for drift in (0.0, 0.2):
                    world = generate_world(
                        n_auditors,
                        malicious_ratio,
                        collusion_strength,
                        drift,
                        seed + ordinal * 101,
                    )
                    for result in evaluate_methods(world, seed + ordinal * 101):
                        rows.append(
                            {
                                "n_auditors": n_auditors,
                                "malicious_ratio": malicious_ratio,
                                "collusion_strength": collusion_strength,
                                "drift": drift,
                                **result,
                            }
                        )
                    ordinal += 1
    primary = [row for row in rows if row["method"] == "gb_three_way"]
    return {
        "metrics": {
            "accuracy": float(np.mean([row["metrics"]["final_audit_accuracy"] for row in primary])),
            "macro_f1": None,
            "auroc": float(np.mean([row["metrics"]["malicious_auroc"] for row in primary])),
            "calibration_error": None,
            "additional": {"rows": rows},
        },
        "structure": {
            "granule_count": int(round(np.mean([row["n_groups"] for row in primary]))),
            "average_granule_size": None,
            "uncertain_sample_ratio": None,
            "additional": {"conditions": 24},
        },
        "outcome": "success",
        "notes": (
            "Synthetic multi-auditor cheap test with identical history/current responses for "
            "all aggregation methods. GB, KMeans, and tree use the same target group count. "
            "Three-way uncertain auditors incur an explicit additional-audit cost."
        ),
    }

