"""Cheap Test E: information compression before HE/MPC/secure aggregation."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
from sklearn.model_selection import train_test_split

from privacy_security.datasets import load_dataset
from secure_aggregation.compression import client_partitions, evaluate_prototypes, summarize_clients


ROOT = Path(__file__).resolve().parents[2]


def run(config: Mapping[str, Any]) -> dict:
    seed = int(config["seed"])
    name = config["dataset_generation_parameters"]["name"]
    dataset = load_dataset(
        name,
        seed=seed,
        cap=int(config["dataset_generation_parameters"].get("cap", 2000)),
        data_home=ROOT / "datasets" / "real" / "openml",
    )
    train_idx, test_idx = train_test_split(
        np.arange(len(dataset.y)),
        test_size=0.3,
        stratify=dataset.y,
        random_state=seed,
    )
    X_train, y_train = dataset.X[train_idx], dataset.y[train_idx]
    X_test, y_test = dataset.X[test_idx], dataset.y[test_idx]
    rows = []
    for n_clients in (5, 10, 20):
        partitions = client_partitions(y_train, n_clients, seed + n_clients, alpha=0.5)
        summaries = summarize_clients(X_train, y_train, partitions, seed + n_clients, purity=0.9)
        metrics_by_method = {
            method: evaluate_prototypes(prototypes, X_test, y_test, len(y_train))
            for method, prototypes in summaries.items()
        }
        raw_accuracy = metrics_by_method["raw"]["accuracy"]
        for method, metrics in metrics_by_method.items():
            rows.append(
                {
                    "n_clients": n_clients,
                    "method": method,
                    "metrics": {
                        **metrics,
                        "accuracy_drop_vs_raw": raw_accuracy - metrics["accuracy"],
                    },
                }
            )
    gb_rows = [row for row in rows if row["method"] == "granular_ball"]
    return {
        "metrics": {
            "accuracy": float(np.mean([row["metrics"]["accuracy"] for row in gb_rows])),
            "macro_f1": None,
            "auroc": None,
            "calibration_error": None,
            "additional": {"rows": rows, "provenance": dataset.provenance},
        },
        "structure": {
            "granule_count": int(round(np.mean([row["metrics"]["n_prototypes"] for row in gb_rows]))),
            "average_granule_size": float(
                np.mean([len(y_train) / row["metrics"]["n_prototypes"] for row in gb_rows])
            ),
            "uncertain_sample_ratio": None,
            "additional": {"feature_dimension": dataset.X.shape[1]},
        },
        "outcome": "success",
        "notes": (
            "Information-compression prototype only. Operation and ciphertext counts are "
            "estimates, not a real cryptographic benchmark. KMeans and MiniBatchKMeans use "
            "the same per-client prototype count as GB. Real HE/MPC is gated on m/n <= 0.1 "
            "and accuracy drop <= 0.02."
        ),
    }

