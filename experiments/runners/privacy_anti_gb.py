"""Anti-GB test for the surviving Privacy Leakage direction."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import pairwise_distances
from sklearn.model_selection import train_test_split

from privacy_security.datasets import load_dataset
from privacy_security.evaluation import evaluate_release
from privacy_security.summaries import all_releases, release_from_groups


ROOT = Path(__file__).resolve().parents[2]


def run(config: Mapping[str, Any]) -> dict:
    seed = int(config["seed"])
    name = config["dataset_generation_parameters"]["name"]
    dataset = load_dataset(name, seed=seed, cap=2000, data_home=ROOT / "datasets" / "real" / "openml")
    indices = np.arange(len(dataset.y))
    strata = np.char.add(dataset.y.astype(str), dataset.sensitive.astype(str))
    member_idx, nonmember_idx = train_test_split(indices, test_size=0.5, random_state=seed, stratify=strata)
    X_member, y_member = dataset.X[member_idx], dataset.y[member_idx]
    X_nonmember, y_nonmember = dataset.X[nonmember_idx], dataset.y[nonmember_idx]
    rows = []
    for purity_threshold in (0.8, 0.9, 0.95):
        standard = all_releases(X_member, y_member, seed=seed, purity=purity_threshold)
        selected = [
            release for release in standard
            if release.variant in {"R8_center_radius_count_purity", "R4_center_radius_count", "matched_full"}
        ]
        gb = next(release for release in selected if release.variant == "R8_center_radius_count_purity")
        k = len(gb.centers)
        tuned = KMeans(n_clusters=k, n_init=50, max_iter=500, random_state=seed).fit_predict(X_member)
        selected.append(release_from_groups("kmeans_tuned", "matched_full", X_member, y_member, _groups(tuned)))
        for linkage in ("complete", "average"):
            labels = AgglomerativeClustering(n_clusters=k, linkage=linkage).fit_predict(X_member)
            selected.append(
                release_from_groups(f"hierarchical_{linkage}", "matched_full", X_member, y_member, _groups(labels))
            )
        oracle_input = np.column_stack([X_member, np.eye(len(np.unique(y_member)))[y_member] * 5.0])
        oracle = KMeans(n_clusters=k, n_init=50, random_state=seed).fit_predict(oracle_input)
        selected.append(release_from_groups("oracle_supervised", "matched_full", X_member, y_member, _groups(oracle)))
        local = _farthest_voronoi(X_member, k, seed)
        selected.append(release_from_groups("knn_local_prototypes", "matched_full", X_member, y_member, local))

        for release in selected:
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
                    "purity_threshold": purity_threshold,
                    "method": release.method,
                    "variant": release.variant,
                    "n_groups": len(release.centers),
                    "metrics": {key: (float(value) if np.isfinite(value) else None) for key, value in metrics.items()},
                }
            )
    primary = [row for row in rows if row["method"] == "granular_ball"]
    return {
        "metrics": {
            "accuracy": float(np.mean([row["metrics"]["utility_accuracy"] for row in primary])),
            "macro_f1": float(np.mean([row["metrics"]["utility_macro_f1"] for row in primary])),
            "auroc": float(np.mean([row["metrics"]["membership_roc_auc"] for row in primary])),
            "calibration_error": None,
            "additional": {"rows": rows, "provenance": dataset.provenance},
        },
        "structure": {
            "granule_count": int(round(np.mean([row["n_groups"] for row in primary]))),
            "average_granule_size": len(member_idx) / np.mean([row["n_groups"] for row in primary]),
            "uncertain_sample_ratio": None,
            "additional": {"purity_scan": [0.8, 0.9, 0.95]},
        },
        "outcome": "success",
        "notes": (
            "Anti-GB test on the two datasets with the strongest exploratory signal. "
            "Every comparator is matched to the GB representative count for each purity. "
            "The supervised oracle partition intentionally receives labels to test whether "
            "GB's label-aware construction, rather than ball geometry, explains the result."
        ),
    }


def _groups(labels: np.ndarray) -> tuple[np.ndarray, ...]:
    return tuple(np.flatnonzero(labels == value) for value in np.unique(labels))


def _farthest_voronoi(X: np.ndarray, k: int, seed: int) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    selected = [int(rng.integers(0, len(X)))]
    distance = pairwise_distances(X, X[selected]).ravel()
    for _ in range(1, k):
        selected.append(int(np.argmax(distance)))
        distance = np.minimum(distance, pairwise_distances(X, X[selected[-1:]]).ravel())
    assignment = np.argmin(pairwise_distances(X, X[selected]), axis=1)
    return _groups(assignment)

