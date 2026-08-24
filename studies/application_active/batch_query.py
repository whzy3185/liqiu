"""Matched batch active-learning selectors with granular-ball attribution."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import (
    load_breast_cancer,
    load_digits,
    load_iris,
    load_wine,
    make_moons,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


DATASETS = ("iris", "wine", "breast_cancer", "digits", "moons")
METHODS = (
    "gb_radius_batch",
    "gb_center_batch",
    "kmeans_batch",
    "entropy",
    "kcenter",
    "random",
)
FRACTIONS = (0.02, 0.05, 0.10, 0.20)


def load_dataset(name: str, seed: int):
    if name == "iris":
        bundle = load_iris()
        return bundle.data.astype(float), bundle.target
    if name == "wine":
        bundle = load_wine()
        return bundle.data.astype(float), bundle.target
    if name == "breast_cancer":
        bundle = load_breast_cancer()
        return bundle.data.astype(float), bundle.target
    if name == "digits":
        bundle = load_digits()
        indices, _ = train_test_split(
            np.arange(len(bundle.target)), train_size=1000, stratify=bundle.target, random_state=seed
        )
        return bundle.data[indices].astype(float), bundle.target[indices]
    if name == "moons":
        return make_moons(n_samples=1000, noise=0.22, random_state=seed)
    raise ValueError(name)


def _entropy(probabilities: np.ndarray) -> np.ndarray:
    values = np.clip(probabilities, 1e-12, 1.0)
    return -np.sum(values * np.log(values), axis=1)


def _gb_groups(features: np.ndarray, count: int, seed: int) -> list[np.ndarray]:
    groups = [np.arange(len(features))]
    split_round = 0
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            local = features[indices]
            center = local.mean(axis=0)
            candidates.append((float(np.sum((local - center) ** 2)), position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates)
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(features[indices])
        children = [indices[labels == value] for value in (0, 1)]
        if min(map(len, children)) == 0:
            break
        groups[position : position + 1] = children
        split_round += 1
    return groups


def _group_query(
    features: np.ndarray,
    uncertainty: np.ndarray,
    groups: list[np.ndarray],
    count: int,
    radius_mode: bool,
) -> np.ndarray:
    selected = []
    ranked_groups = sorted(
        groups,
        key=lambda indices: float(np.mean(uncertainty[indices]) * np.sqrt(len(indices))),
        reverse=True,
    )
    for indices in ranked_groups[:count]:
        local = features[indices]
        center = local.mean(axis=0)
        distances = np.linalg.norm(local - center, axis=1)
        if radius_mode:
            radius = max(float(np.quantile(distances, 0.95)), 1e-6)
            score = uncertainty[indices] * (1.0 + distances / radius)
        else:
            score = uncertainty[indices]
        selected.append(int(indices[int(np.argmax(score))]))
    if len(selected) < count:
        remaining = np.setdiff1d(np.arange(len(features)), selected, assume_unique=False)
        fill = remaining[np.argsort(-uncertainty[remaining])[: count - len(selected)]]
        selected.extend(map(int, fill))
    return np.asarray(selected[:count], dtype=int)


def _kmeans_query(features, uncertainty, count, seed):
    labels = KMeans(count, n_init=5, random_state=seed).fit_predict(features)
    groups = [np.flatnonzero(labels == label) for label in range(count)]
    return _group_query(features, uncertainty, groups, count, False)


def _kcenter_query(pool, labeled, count):
    minimum = np.linalg.norm(pool[:, None, :] - labeled[None, :, :], axis=2).min(axis=1)
    selected = []
    for _ in range(count):
        choice = int(np.argmax(minimum))
        selected.append(choice)
        distance = np.linalg.norm(pool - pool[choice], axis=1)
        minimum = np.minimum(minimum, distance)
        minimum[selected] = -np.inf
    return np.asarray(selected)


def _model(seed):
    return LogisticRegression(max_iter=2000, random_state=seed)


def _curve_auc(curve: list[dict[str, float]], metric: str) -> float:
    x = np.asarray([row["fraction"] for row in curve])
    y = np.asarray([row[metric] for row in curve])
    if len(np.unique(x)) == 1:
        return float(y.mean())
    return float(np.trapezoid(y, x) / (x[-1] - x[0]))


def evaluate_batch_active_learning(dataset: str, seed: int):
    features, labels = load_dataset(dataset, seed)
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    scaler = StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)
    rng = np.random.default_rng(seed + 101)
    initial = []
    for label in np.unique(train_y):
        candidates = np.flatnonzero(train_y == label)
        initial.extend(rng.choice(candidates, min(2, len(candidates)), replace=False))
    initial = np.asarray(sorted(set(initial)), dtype=int)
    target_counts = sorted(
        set(max(len(initial), int(np.ceil(fraction * len(train_y)))) for fraction in FRACTIONS)
    )
    rows = []
    for method_index, method in enumerate(METHODS):
        labeled = initial.copy()
        pool = np.setdiff1d(np.arange(len(train_y)), labeled)
        curve = []
        query_seconds = 0.0
        for target_count in target_counts:
            if len(labeled) < target_count:
                classifier = _model(seed).fit(train_x[labeled], train_y[labeled])
                uncertainty = _entropy(classifier.predict_proba(train_x[pool]))
                count = min(target_count - len(labeled), len(pool))
                start = time.perf_counter()
                if method == "gb_radius_batch":
                    groups = _gb_groups(train_x[pool], count, seed + target_count)
                    local = _group_query(train_x[pool], uncertainty, groups, count, True)
                elif method == "gb_center_batch":
                    groups = _gb_groups(train_x[pool], count, seed + target_count)
                    local = _group_query(train_x[pool], uncertainty, groups, count, False)
                elif method == "kmeans_batch":
                    local = _kmeans_query(train_x[pool], uncertainty, count, seed + target_count)
                elif method == "entropy":
                    local = np.argsort(-uncertainty)[:count]
                elif method == "kcenter":
                    local = _kcenter_query(train_x[pool], train_x[labeled], count)
                elif method == "random":
                    local = np.random.default_rng(seed + 1009 * method_index + target_count).choice(
                        len(pool), count, replace=False
                    )
                else:
                    raise ValueError(method)
                query_seconds += time.perf_counter() - start
                chosen = pool[local]
                labeled = np.concatenate([labeled, chosen])
                pool = np.setdiff1d(pool, chosen)
            classifier = _model(seed).fit(train_x[labeled], train_y[labeled])
            prediction = classifier.predict(test_x)
            curve.append(
                {
                    "labeled": int(len(labeled)),
                    "fraction": float(len(labeled) / len(train_y)),
                    "accuracy": float(accuracy_score(test_y, prediction)),
                    "macro_f1": float(f1_score(test_y, prediction, average="macro", zero_division=0)),
                }
            )
        rows.append(
            {
                "method": method,
                "curve": curve,
                "accuracy_auc": _curve_auc(curve, "accuracy"),
                "macro_f1_auc": _curve_auc(curve, "macro_f1"),
                "query_seconds": query_seconds,
            }
        )
    return {"dataset": dataset, "seed": seed, "train_size": len(train_y), "methods": rows}
