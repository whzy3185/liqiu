"""Frozen v1 structural diagnostics for metadata-approved numeric candidates."""

from __future__ import annotations

import json

import numpy as np
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


K_VALUES = (5, 10, 20)


def _safe_cv(values: np.ndarray) -> float:
    mean = float(np.mean(values))
    return float(np.std(values) / mean) if mean > 0 else 0.0


def _effective_rank(x: np.ndarray) -> tuple[float, float]:
    covariance = np.cov(x, rowvar=False)
    values = np.clip(np.linalg.eigvalsh(covariance), 0, None)
    if values.sum() <= 0:
        return 0.0, 0.0
    probabilities = values / values.sum()
    positive = probabilities[probabilities > 0]
    rank = float(np.exp(-(positive * np.log(positive)).sum()))
    return rank, rank / x.shape[1]


def _correlation_stats(x: np.ndarray) -> tuple[float, float]:
    if x.shape[1] < 2:
        return 0.0, 0.0
    corr = np.nan_to_num(np.corrcoef(x, rowvar=False), nan=0.0)
    upper = np.abs(corr[np.triu_indices_from(corr, 1)])
    return float(upper.mean()), float((upper >= .90).mean())


def _neighbours(x: np.ndarray, y: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    n_neighbors = min(k + 1, len(x))
    distances, indices = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean").fit(x).kneighbors(x)
    return distances[:, -1], indices[:, 1:]


def _local_labels(y: np.ndarray, neighbour_indices: np.ndarray, n_classes: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    neighbour_y = y[neighbour_indices]
    proportions = np.empty((len(y), n_classes), dtype=float)
    for class_id in range(n_classes):
        proportions[:, class_id] = (neighbour_y == class_id).mean(axis=1)
    disagreement = 1 - proportions.max(axis=1)
    log_proportions = np.zeros_like(proportions)
    positive = proportions > 0
    log_proportions[positive] = np.log(proportions[positive])
    entropy = -(proportions * log_proportions).sum(axis=1)
    entropy /= np.log(n_classes) if n_classes > 1 else 1
    return disagreement, entropy, proportions


def profile_numeric(x: np.ndarray, y: np.ndarray) -> dict[str, object]:
    """Return v1 diagnostics; intended only before any membership experiment."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y)
    missing_rate = float(np.isnan(x).mean())
    x = SimpleImputer(strategy="median").fit_transform(x)
    x = StandardScaler().fit_transform(x)
    _, encoded = np.unique(y, return_inverse=True)
    classes, counts = np.unique(encoded, return_counts=True)
    n, d = x.shape
    effective_rank, effective_ratio = _effective_rank(x)
    mean_corr, high_corr = _correlation_stats(x)
    output: dict[str, object] = {
        "n": n,
        "d": d,
        "raw_dimension": d,
        "n_classes": len(classes),
        "class_distribution": json.dumps(counts.tolist()),
        "imbalance_ratio": float(counts.max() / counts.min()),
        "missing_rate": missing_rate,
        "duplicate_rate": float(1 - len(np.unique(x, axis=0)) / n),
        "effective_rank": effective_rank,
        "effective_rank_ratio": effective_ratio,
        "mean_absolute_feature_correlation": mean_corr,
        "high_correlation_pair_fraction": high_corr,
    }
    conflict_values = []
    per_k = {}
    for k in K_VALUES:
        if n <= k:
            continue
        distances, indices = _neighbours(x, encoded, k)
        disagreement, entropy, proportions = _local_labels(encoded, indices, len(classes))
        class_distances = [distances[encoded == class_id].mean() for class_id in classes]
        if np.all(disagreement == 0):
            conflict = 0.0
        else:
            conflict = float(((distances <= np.quantile(distances, .25)) & (disagreement >= np.quantile(disagreement, .75)) & (disagreement > 0)).mean())
        per_k[k] = {"distance": distances, "disagreement": disagreement, "entropy": entropy, "proportions": proportions}
        output.update({
            f"knn_distance_mean_k{k}": float(distances.mean()),
            f"knn_distance_median_k{k}": float(np.median(distances)),
            f"knn_distance_cv_k{k}": _safe_cv(distances),
            f"class_density_dispersion_k{k}": _safe_cv(np.asarray(class_distances)),
            f"local_disagreement_k{k}": float(disagreement.mean()),
            f"knn_label_entropy_k{k}": float(entropy.mean()),
            f"geometry_label_conflict_k{k}": conflict,
        })
        conflict_values.append(conflict)
    if 10 in per_k:
        output["boundary_sample_fraction_k10"] = float((per_k[10]["disagreement"] >= .20).mean())
        class_support_median = np.median(counts)
        minority_classes = classes[counts <= class_support_median]
        minority_islands = []
        proportions = per_k[10]["proportions"]
        for class_id in minority_classes:
            mask = encoded == class_id
            minority_islands.append(float((proportions[mask, class_id] < .50).mean()))
        output["minority_island_proxy"] = float(np.mean(minority_islands))
    else:
        output["boundary_sample_fraction_k10"] = float("nan")
        output["minority_island_proxy"] = float("nan")
    multi = []
    for class_id, support in zip(classes, counts, strict=True):
        if support < 2 * max(K_VALUES):
            continue
        group = x[encoded == class_id]
        inertia_one = float(((group - group.mean(axis=0)) ** 2).sum())
        if inertia_one > 0:
            inertia_two = KMeans(n_clusters=2, n_init=10, random_state=17).fit(group).inertia_
            multi.append(1 - inertia_two / inertia_one)
    output["multimodality_proxy"] = float(np.mean(multi)) if multi else float("nan")
    output["geometry_label_conflict_mean"] = float(np.mean(conflict_values)) if conflict_values else float("nan")
    return output
