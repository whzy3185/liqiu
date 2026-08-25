"""Approximate deletion by updating only fixed regional sufficient statistics."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, load_wine
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from studies.risk_granularity.tree import GranulationTree


DATASETS = ("breast_cancer", "wine", "digits", "satimage")
METHODS = ("granular_ball", "kmeans", "decision_tree")
SCENARIOS = ("random", "local_concentrated", "class_skew")


def _load(dataset, seed, max_samples=1200):
    if dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "wine":
        bundle = load_wine()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "satimage":
        bundle = fetch_openml(data_id=182, as_frame=False, parser="auto")
        features = np.asarray(bundle.data, float)
        labels = LabelEncoder().fit_transform(bundle.target)
    else:
        raise ValueError(dataset)
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    return features, np.asarray(labels, int)


def _representation(features, labels, groups, classes, radii=True):
    centers = []
    radius_values = []
    counts = []
    valid_groups = []
    for group in groups:
        if len(group) == 0:
            continue
        local = features[group]
        center = local.mean(axis=0)
        centers.append(center)
        radius_values.append(
            max(float(np.mean(np.linalg.norm(local - center, axis=1))), 1e-9) if radii else 0.0
        )
        counts.append(np.bincount(labels[group], minlength=classes))
        valid_groups.append(np.asarray(group))
    return {
        "centers": np.vstack(centers),
        "radii": np.asarray(radius_values),
        "counts": np.asarray(counts, float),
        "groups": valid_groups,
    }


def _predict_proba(representation, query, surface):
    distances = np.linalg.norm(
        query[:, None, :] - representation["centers"][None, :, :], axis=2
    )
    if surface:
        distances -= representation["radii"][None, :]
    assigned = np.argmin(distances, axis=1)
    counts = representation["counts"][assigned]
    return counts / np.maximum(counts.sum(axis=1, keepdims=True), 1)


def _fit_gb(features, labels, seed, tau=0.85):
    tree = GranulationTree(random_state=seed, split_method="kmeans").fit(features, labels)
    leaves = tree.cut(tau)
    return [leaf.indices for leaf in leaves]


def _fit_kmeans(features, labels, count, seed):
    assignments = KMeans(count, n_init=10, random_state=seed).fit_predict(features)
    return [np.flatnonzero(assignments == group) for group in range(count)]


def _fit_tree(features, labels, count, seed):
    tree = DecisionTreeClassifier(
        max_leaf_nodes=max(2, count), min_samples_leaf=2, random_state=seed
    ).fit(features, labels)
    leaf = tree.apply(features)
    groups = [np.flatnonzero(leaf == value) for value in np.unique(leaf)]
    return tree, groups


def _delete_mask(scenario, labels, gb_groups, seed, rate=0.10):
    rng = np.random.default_rng(seed)
    target = max(1, int(round(rate * len(labels))))
    deleted = np.zeros(len(labels), dtype=bool)
    if scenario == "random":
        deleted[rng.choice(len(labels), target, replace=False)] = True
    elif scenario == "local_concentrated":
        ordered = sorted(gb_groups, key=len, reverse=True)
        selected = []
        for group in ordered:
            take = min(len(group), target - len(selected))
            selected.extend(rng.choice(group, take, replace=False))
            if len(selected) == target:
                break
        deleted[selected] = True
    elif scenario == "class_skew":
        counts = np.bincount(labels)
        for label in np.argsort(counts):
            candidates = np.flatnonzero(labels == label)
            maximum = max(0, len(candidates) - 2)
            take = min(maximum, target - deleted.sum())
            if take:
                deleted[rng.choice(candidates, take, replace=False)] = True
            if deleted.sum() == target:
                break
    else:
        raise ValueError(scenario)
    return deleted


def _fixed_update(features, labels, original_groups, deleted, classes, radii):
    groups = [group[~deleted[group]] for group in original_groups]
    return _representation(features, labels, groups, classes, radii=radii)


def _evaluate_method(method, train_x, train_y, test_x, test_y, initial, deleted, count, seed):
    classes = len(np.unique(train_y))
    start = time.perf_counter()
    if method == "decision_tree":
        tree, groups = initial
        fixed = _fixed_update(train_x, train_y, groups, deleted, classes, radii=False)
        # A fixed tree routes queries to original leaves; represent each leaf by its
        # recomputed center for a common regional-prototype comparison.
        approx_prob = _predict_proba(fixed, test_x, surface=False)
    else:
        groups = initial
        fixed = _fixed_update(
            train_x, train_y, groups, deleted, classes, radii=method == "granular_ball"
        )
        approx_prob = _predict_proba(fixed, test_x, surface=method == "granular_ball")
    update_seconds = time.perf_counter() - start

    keep = ~deleted
    start = time.perf_counter()
    if method == "granular_ball":
        fresh_groups = _fit_gb(train_x[keep], train_y[keep], seed + 100)
        fresh = _representation(
            train_x[keep], train_y[keep], fresh_groups, classes, radii=True
        )
        full_prob = _predict_proba(fresh, test_x, surface=True)
    elif method == "kmeans":
        fresh_groups = _fit_kmeans(train_x[keep], train_y[keep], count, seed + 100)
        fresh = _representation(
            train_x[keep], train_y[keep], fresh_groups, classes, radii=False
        )
        full_prob = _predict_proba(fresh, test_x, surface=False)
    else:
        _, fresh_groups = _fit_tree(train_x[keep], train_y[keep], count, seed + 100)
        fresh = _representation(
            train_x[keep], train_y[keep], fresh_groups, classes, radii=False
        )
        full_prob = _predict_proba(fresh, test_x, surface=False)
    retrain_seconds = time.perf_counter() - start
    approx_prediction = approx_prob.argmax(axis=1)
    full_prediction = full_prob.argmax(axis=1)
    return {
        "method": method,
        "agreement_with_full_retrain": float(np.mean(approx_prediction == full_prediction)),
        "probability_l1_vs_full": float(np.mean(np.abs(approx_prob - full_prob))),
        "approx_accuracy": float(accuracy_score(test_y, approx_prediction)),
        "full_retrain_accuracy": float(accuracy_score(test_y, full_prediction)),
        "accuracy_gap_vs_full": float(
            accuracy_score(test_y, approx_prediction) - accuracy_score(test_y, full_prediction)
        ),
        "update_seconds": update_seconds,
        "full_retrain_seconds": retrain_seconds,
        "speedup": retrain_seconds / max(update_seconds, 1e-12),
        "initial_groups": count,
        "updated_groups": len(fixed["groups"]),
        "fresh_groups": len(fresh["groups"]),
    }


def evaluate_local_unlearning(dataset: str, seed: int):
    features, labels = _load(dataset, seed)
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    scaler = StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)
    gb_groups = _fit_gb(train_x, train_y, seed + 10)
    count = max(2, len(gb_groups))
    initial = {
        "granular_ball": gb_groups,
        "kmeans": _fit_kmeans(train_x, train_y, count, seed + 20),
        "decision_tree": _fit_tree(train_x, train_y, count, seed + 30),
    }
    rows = []
    for scenario in SCENARIOS:
        deleted = _delete_mask(scenario, train_y, gb_groups, seed + 40 + SCENARIOS.index(scenario))
        for method in METHODS:
            rows.append(
                {
                    "scenario": scenario,
                    "deleted": int(deleted.sum()),
                    "deletion_fraction": float(deleted.mean()),
                    **_evaluate_method(
                        method,
                        train_x,
                        train_y,
                        test_x,
                        test_y,
                        initial[method],
                        deleted,
                        count,
                        seed + 50 + METHODS.index(method),
                    ),
                }
            )
    return {"dataset": dataset, "seed": seed, "train_items": len(train_y), "initial_gb_groups": count, "frontier": rows}
