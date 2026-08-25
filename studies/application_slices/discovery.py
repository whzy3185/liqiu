"""Discover validation-error regions and verify them on an independent test set."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from studies.risk_granularity.tree import GranulationTree


DATASETS = ("moons", "breast_cancer", "digits", "satimage")
METHODS = ("granular_ball", "kmeans", "error_tree", "knn_density", "random_cells")


def _load(dataset, seed, max_samples=1200):
    if dataset == "moons":
        features, labels = make_moons(n_samples=max_samples, noise=0.25, random_state=seed)
    elif dataset == "breast_cancer":
        bundle = load_breast_cancer()
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


def _hidden_region(validation_x, test_x):
    first = validation_x[:, 0]
    second = validation_x[:, min(1, validation_x.shape[1] - 1)]
    score = first * second + 0.35 * first**2
    threshold = float(np.quantile(score, 0.75))
    return score >= threshold, (
        test_x[:, 0] * test_x[:, min(1, test_x.shape[1] - 1)] + 0.35 * test_x[:, 0] ** 2
    ) >= threshold


def _corrupt(features, selected, important, rng):
    output = features.copy()
    if selected.any():
        width = min(5, len(important))
        columns = important[:width]
        output[np.ix_(selected, columns)] += rng.normal(0, 2.5, size=(selected.sum(), width))
    return output


def _gb_assign(validation_x, errors, test_x, seed):
    tree = GranulationTree(random_state=seed, split_method="kmeans").fit(validation_x, errors)
    leaves = tree.cut(0.98)
    if len(leaves) > 40:
        leaves = tree.cut(0.95)
    centers = np.vstack([leaf.center for leaf in leaves])
    radii = np.asarray([leaf.radius for leaf in leaves])
    distances = np.linalg.norm(test_x[:, None, :] - centers[None, :, :], axis=2) - radii[None, :]
    return [leaf.indices for leaf in leaves], np.argmin(distances, axis=1), len(leaves)


def _kmeans_assign(validation_x, test_x, count, seed):
    model = KMeans(count, n_init=10, random_state=seed).fit(validation_x)
    groups = [np.flatnonzero(model.labels_ == label) for label in range(count)]
    return groups, model.predict(test_x)


def _tree_assign(validation_x, errors, test_x, count, seed):
    model = DecisionTreeClassifier(
        max_leaf_nodes=max(2, count), min_samples_leaf=10, random_state=seed
    ).fit(validation_x, errors)
    validation_leaf = model.apply(validation_x)
    test_leaf = model.apply(test_x)
    values = np.unique(validation_leaf)
    mapping = {value: index for index, value in enumerate(values)}
    groups = [np.flatnonzero(validation_leaf == value) for value in values]
    return groups, np.asarray([mapping.get(value, 0) for value in test_leaf])


def _random_assign(validation_x, test_x, count, seed):
    rng = np.random.default_rng(seed)
    projection = rng.normal(size=(validation_x.shape[1], max(2, int(np.ceil(np.log2(count))))))
    validation_code = (validation_x @ projection > 0).dot(1 << np.arange(projection.shape[1]))
    test_code = (test_x @ projection > 0).dot(1 << np.arange(projection.shape[1]))
    values, counts = np.unique(validation_code, return_counts=True)
    values = values[np.argsort(-counts)[:count]]
    groups = [np.flatnonzero(validation_code == value) for value in values]
    centers = np.vstack([validation_x[group].mean(axis=0) for group in groups])
    assigned = np.empty(len(test_x), dtype=int)
    for item, code in enumerate(test_code):
        matches = np.flatnonzero(values == code)
        assigned[item] = int(matches[0]) if len(matches) else int(
            np.argmin(np.linalg.norm(test_x[item] - centers, axis=1))
        )
    return groups, assigned


def _select_groups(groups, errors, target_coverage=0.20):
    global_error = float(errors.mean())
    ranked = sorted(
        range(len(groups)),
        key=lambda group: (errors[groups[group]].sum() + 2 * global_error) / (len(groups[group]) + 2),
        reverse=True,
    )
    selected = []
    covered = 0
    target = int(np.ceil(target_coverage * len(errors)))
    for group in ranked:
        selected.append(group)
        covered += len(groups[group])
        if covered >= target:
            break
    return set(selected)


def _fixed_coverage_selection(groups, assignment, errors, coverage=0.20):
    global_error = float(errors.mean())
    risk = np.asarray(
        [
            (errors[group].sum() + 2 * global_error) / (len(group) + 2)
            for group in groups
        ]
    )
    score = risk[assignment]
    count = max(1, int(np.ceil(coverage * len(assignment))))
    selected = np.zeros(len(assignment), dtype=bool)
    selected[np.argsort(-score)[:count]] = True
    return selected


def _metrics(selected, errors, hidden):
    global_risk = float(errors.mean())
    risk = float(errors[selected].mean()) if selected.any() else 0.0
    return {
        "coverage": float(selected.mean()),
        "selected_risk": risk,
        "risk_uplift": risk - global_risk,
        "error_recall": float(errors[selected].sum() / max(errors.sum(), 1)),
        "hidden_region_precision": float(hidden[selected].mean()) if selected.any() else 0.0,
    }


def evaluate_failure_slices(dataset: str, seed: int):
    features, labels = _load(dataset, seed)
    train_x, remainder_x, train_y, remainder_y = train_test_split(
        features, labels, test_size=0.50, stratify=labels, random_state=seed
    )
    validation_x, test_x, validation_y, test_y = train_test_split(
        remainder_x, remainder_y, test_size=0.50, stratify=remainder_y, random_state=seed + 1
    )
    scaler = StandardScaler().fit(train_x)
    train_x, validation_x, test_x = map(scaler.transform, (train_x, validation_x, test_x))
    model = LogisticRegression(max_iter=2000, random_state=seed).fit(train_x, train_y)
    importance = np.argsort(-np.max(np.abs(model.coef_), axis=0))
    hidden_validation, hidden_test = _hidden_region(validation_x, test_x)
    rng = np.random.default_rng(seed + 10)
    validation_corrupt = _corrupt(validation_x, hidden_validation, importance, rng)
    test_corrupt = _corrupt(test_x, hidden_test, importance, rng)
    validation_errors = (model.predict(validation_corrupt) != validation_y).astype(int)
    test_errors = (model.predict(test_corrupt) != test_y).astype(int)

    start = time.perf_counter()
    gb_groups, gb_test_assignment, count = _gb_assign(
        validation_corrupt, validation_errors, test_corrupt, seed + 20
    )
    assignments = {"granular_ball": (gb_groups, gb_test_assignment, time.perf_counter() - start)}
    for method, function in (
        ("kmeans", _kmeans_assign),
        ("error_tree", _tree_assign),
        ("random_cells", _random_assign),
    ):
        start = time.perf_counter()
        groups, assigned = function(
            validation_corrupt,
            validation_errors,
            test_corrupt,
            count,
            seed + 30 + METHODS.index(method),
        ) if method == "error_tree" else function(
            validation_corrupt,
            test_corrupt,
            count,
            seed + 30 + METHODS.index(method),
        )
        assignments[method] = (groups, assigned, time.perf_counter() - start)

    rows = []
    for method in ("granular_ball", "kmeans", "error_tree", "random_cells"):
        groups, test_assignment, runtime = assignments[method]
        selected = _fixed_coverage_selection(groups, test_assignment, validation_errors)
        rows.append({"method": method, "regions": len(groups), "runtime_seconds": runtime, **_metrics(selected, test_errors, hidden_test)})

    start = time.perf_counter()
    neighbors = min(30, len(validation_x))
    ids = NearestNeighbors(n_neighbors=neighbors).fit(validation_corrupt).kneighbors(
        test_corrupt, return_distance=False
    )
    score = validation_errors[ids].mean(axis=1)
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(-score)[: max(1, int(np.ceil(0.20 * len(score))))]] = True
    rows.append(
        {
            "method": "knn_density",
            "regions": None,
            "runtime_seconds": time.perf_counter() - start,
            **_metrics(selected, test_errors, hidden_test),
        }
    )
    return {
        "dataset": dataset,
        "seed": seed,
        "validation_error_rate": float(validation_errors.mean()),
        "test_error_rate": float(test_errors.mean()),
        "hidden_test_fraction": float(hidden_test.mean()),
        "frontier": rows,
    }
