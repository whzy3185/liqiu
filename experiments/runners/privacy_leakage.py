"""Cheap Test A: leakage from released tabular granular summaries."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
from sklearn.model_selection import train_test_split

from privacy_security.datasets import load_dataset
from privacy_security.evaluation import evaluate_release
from privacy_security.summaries import all_releases


ROOT = Path(__file__).resolve().parents[2]


def run(config: Mapping[str, Any]) -> dict:
    seed = int(config["seed"])
    parameters = config["dataset_generation_parameters"]
    dataset = load_dataset(
        parameters["name"],
        seed=seed,
        cap=int(parameters.get("cap", 2000)),
        data_home=ROOT / "datasets" / "real" / "openml",
    )
    indices = np.arange(len(dataset.y))
    strata = np.char.add(dataset.y.astype(str), dataset.sensitive.astype(str))
    member_idx, nonmember_idx = train_test_split(
        indices,
        test_size=0.5,
        random_state=seed,
        stratify=strata,
    )
    X_member, y_member = dataset.X[member_idx], dataset.y[member_idx]
    X_nonmember, y_nonmember = dataset.X[nonmember_idx], dataset.y[nonmember_idx]
    releases = all_releases(
        X_member,
        y_member,
        seed=seed,
        purity=float(config["hyperparameters"].get("purity", 0.9)),
    )
    rows = []
    for release in releases:
        metrics = evaluate_release(
            release,
            X_member,
            y_member,
            X_nonmember,
            y_nonmember,
            dataset.sensitive[member_idx],
            dataset.sensitive_index,
            seed=seed,
        )
        rows.append(
            {
                "method": release.method,
                "variant": release.variant,
                "n_groups": len(release.centers),
                "metrics": _json_safe(metrics),
            }
        )

    primary = next(row for row in rows if row["variant"] == "R8_center_radius_count_purity")
    return {
        "metrics": {
            "accuracy": primary["metrics"]["utility_accuracy"],
            "macro_f1": primary["metrics"]["utility_macro_f1"],
            "auroc": primary["metrics"]["membership_roc_auc"],
            "calibration_error": None,
            "additional": {
                "releases": rows,
                "sensitive_attribute": dataset.sensitive_name,
                "provenance": dataset.provenance,
                "member_count": len(member_idx),
                "nonmember_count": len(nonmember_idx),
            },
        },
        "structure": {
            "granule_count": primary["n_groups"],
            "average_granule_size": len(member_idx) / primary["n_groups"],
            "uncertain_sample_ratio": None,
            "additional": {
                "feature_dimension": dataset.X.shape[1],
                "matched_group_target": primary["n_groups"],
            },
        },
        "outcome": "success",
        "notes": (
            "Exploration-pool empirical attack benchmark. Privacy metrics are not DP, "
            "information-theoretic, or cryptographic guarantees. KMeans, hierarchical, "
            "random, and tree controls receive the same member split; representative count "
            "is matched to the GB count except when a tree cannot realize every requested leaf."
        ),
    }


def _json_safe(values: Mapping[str, float]) -> dict:
    return {key: (float(value) if np.isfinite(value) else None) for key, value in values.items()}

