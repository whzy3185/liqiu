from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import spearmanr, wasserstein_distance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from sklearn.metrics import pairwise_distances
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from privacy_security.summaries import ReleasedSummary


def evaluate_release(
    release: ReleasedSummary,
    X_member: np.ndarray,
    y_member: np.ndarray,
    X_nonmember: np.ndarray,
    y_nonmember: np.ndarray,
    sensitive_member: np.ndarray,
    sensitive_index: int,
    *,
    seed: int,
) -> dict:
    queries = np.vstack([X_member, X_nonmember])
    membership = np.r_[np.ones(len(X_member), dtype=int), np.zeros(len(X_nonmember), dtype=int)]
    features, nearest = _attack_features(release, queries)
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        probabilities = cross_val_predict(
            LogisticRegression(max_iter=1000, class_weight="balanced"),
            features,
            membership,
            cv=splitter,
            method="predict_proba",
        )[:, 1]

    utility_prediction = _prototype_predict(release, X_nonmember)
    reconstructed = release.centers[_nearest(release, X_member)]
    public = np.delete(X_member, sensitive_index, axis=1)
    public_centers = np.delete(release.centers, sensitive_index, axis=1)
    sensitive_nearest = np.argmin(pairwise_distances(public, public_centers), axis=1)
    sensitive_estimate = (release.centers[sensitive_nearest, sensitive_index] > 0).astype(int)

    per_ball_attack = []
    member_nearest = nearest[: len(X_member)]
    for ball_id in range(len(release.centers)):
        mask = member_nearest == ball_id
        if np.any(mask):
            per_ball_attack.append(
                (
                    release.counts[ball_id],
                    release.radii[ball_id],
                    release.purities[ball_id],
                    float(probabilities[: len(X_member)][mask].mean()),
                )
            )
    correlations = _ball_correlations(per_ball_attack)
    return {
        "membership_roc_auc": float(roc_auc_score(membership, probabilities)),
        "membership_pr_auc": float(average_precision_score(membership, probabilities)),
        "membership_accuracy": float(accuracy_score(membership, probabilities >= 0.5)),
        "attribute_accuracy": float(accuracy_score(sensitive_member, sensitive_estimate)),
        "attribute_macro_f1": float(f1_score(sensitive_member, sensitive_estimate, average="macro")),
        "attribute_auc": _safe_auc(sensitive_member, release.centers[sensitive_nearest, sensitive_index]),
        "reconstruction_mse": float(np.mean((X_member - reconstructed) ** 2)),
        "reconstruction_nn_distance": float(np.linalg.norm(X_member - reconstructed, axis=1).mean()),
        "distribution_wasserstein": float(
            np.mean([wasserstein_distance(X_member[:, j], reconstructed[:, j]) for j in range(X_member.shape[1])])
        ),
        "utility_accuracy": float(accuracy_score(y_nonmember, utility_prediction)),
        "utility_macro_f1": float(f1_score(y_nonmember, utility_prediction, average="macro")),
        "compression_ratio": float(len(release.centers) / len(X_member)),
        **correlations,
    }


def _attack_features(release: ReleasedSummary, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    distances = pairwise_distances(X, release.centers)
    order = np.argpartition(distances, kth=min(1, distances.shape[1] - 1), axis=1)
    nearest = order[:, 0]
    first = distances[np.arange(len(X)), nearest]
    if distances.shape[1] > 1:
        second = np.partition(distances, 1, axis=1)[:, 1]
    else:
        second = first
    features = [first, second - first]
    if release.disclose_radius:
        features.append(first / release.radii[nearest])
    if release.disclose_count:
        features.append(np.log1p(release.counts[nearest]))
    if release.disclose_purity:
        features.append(release.purities[nearest])
    return np.column_stack(features), nearest


def _nearest(release: ReleasedSummary, X: np.ndarray) -> np.ndarray:
    distances = pairwise_distances(X, release.centers)
    if release.disclose_radius:
        distances = distances - release.radii[None, :]
    return np.argmin(distances, axis=1)


def _prototype_predict(release: ReleasedSummary, X: np.ndarray) -> np.ndarray:
    return release.labels[_nearest(release, X)]


def _safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score)) if len(np.unique(y)) == 2 else float("nan")


def _ball_correlations(rows: list[tuple[float, float, float, float]]) -> dict:
    names = ("ball_size_attack_spearman", "radius_attack_spearman", "purity_attack_spearman")
    if len(rows) < 4:
        return dict.fromkeys(names, float("nan"))
    values = np.asarray(rows)
    result = {}
    for index, name in enumerate(names):
        if len(np.unique(values[:, index])) < 2 or len(np.unique(values[:, 3])) < 2:
            result[name] = float("nan")
            continue
        coefficient = spearmanr(values[:, index], values[:, 3]).statistic
        result[name] = float(coefficient) if np.isfinite(coefficient) else float("nan")
    return result
