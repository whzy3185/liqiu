"""Local-region recovery of a missing feature view at inference time."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, load_wine
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from studies.application_cleaning.cell_context import build_context_tree


DATASETS = ("satimage", "digits", "breast_cancer", "wine")
METHODS = ("gb_multiscale", "gb_terminal", "kmeans", "knn", "decision_tree", "ridge", "global_mean")
MISSING_RATES = (0.20, 0.40, 0.60)


def _load(dataset, seed, max_samples=2400):
    if dataset == "satimage":
        bundle = fetch_openml(data_id=182, as_frame=False, parser="auto")
        features = np.asarray(bundle.data, float)
        labels = LabelEncoder().fit_transform(bundle.target)
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "wine":
        bundle = load_wine()
        features, labels = bundle.data.astype(float), bundle.target
    else:
        raise ValueError(dataset)
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    split = features.shape[1] // 2
    return features[:, :split], features[:, split:], np.asarray(labels, int)


def _route(tree, cut, query):
    centers = np.vstack([tree.nodes[node].center for node in cut])
    radii = np.asarray([tree.nodes[node].radius for node in cut])
    distances = np.linalg.norm(query[:, None, :] - centers[None, :, :], axis=2)
    distances = (distances - radii[None, :]) / radii[None, :]
    return np.asarray(cut)[np.argmin(distances, axis=1)]


def _gb_predict(tree, target_view, query, multiscale):
    stats = np.vstack([target_view[node.indices].mean(axis=0) for node in tree.nodes])
    cuts = tree.cuts()
    if not multiscale:
        cuts = [cuts[-1]]
    predictions = []
    for cut in cuts:
        predictions.append(stats[_route(tree, cut, query)])
    weights = np.arange(1, len(predictions) + 1, dtype=float)
    weights /= weights.sum()
    return np.sum(np.asarray(predictions) * weights[:, None, None], axis=0)


def _fit_predictors(train_a, train_b, query_a, seed):
    min_leaf = max(10, int(np.ceil(0.05 * len(train_a))))
    budget = min(16, max(4, len(train_a) // 40))
    tree = build_context_tree(train_a, budget, seed, min_leaf)
    count = len(tree.leaves)
    output = {}
    timings = {}

    start = time.perf_counter()
    output["gb_multiscale"] = _gb_predict(tree, train_b, query_a, True)
    timings["gb_multiscale"] = time.perf_counter() - start
    start = time.perf_counter()
    output["gb_terminal"] = _gb_predict(tree, train_b, query_a, False)
    timings["gb_terminal"] = time.perf_counter() - start

    start = time.perf_counter()
    model = KMeans(count, n_init=10, random_state=seed + 1).fit(train_a)
    means = np.vstack([train_b[model.labels_ == label].mean(axis=0) for label in range(count)])
    output["kmeans"] = means[model.predict(query_a)]
    timings["kmeans"] = time.perf_counter() - start

    start = time.perf_counter()
    neighbors = min(50, max(10, len(train_a) // max(count, 1)))
    ids = NearestNeighbors(n_neighbors=neighbors).fit(train_a).kneighbors(
        query_a, return_distance=False
    )
    output["knn"] = train_b[ids].mean(axis=1)
    timings["knn"] = time.perf_counter() - start

    start = time.perf_counter()
    decision = DecisionTreeRegressor(
        max_leaf_nodes=max(2, count), min_samples_leaf=min_leaf, random_state=seed + 2
    ).fit(train_a, train_b)
    output["decision_tree"] = decision.predict(query_a)
    timings["decision_tree"] = time.perf_counter() - start

    start = time.perf_counter()
    output["ridge"] = Ridge(alpha=1.0).fit(train_a, train_b).predict(query_a)
    timings["ridge"] = time.perf_counter() - start
    start = time.perf_counter()
    output["global_mean"] = np.tile(train_b.mean(axis=0), (len(query_a), 1))
    timings["global_mean"] = time.perf_counter() - start
    return output, timings, count


def evaluate_missing_view(dataset: str, seed: int):
    view_a, view_b, labels = _load(dataset, seed)
    train_a, test_a, train_b, test_b, train_y, test_y = train_test_split(
        view_a, view_b, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    scaler_a = StandardScaler().fit(train_a)
    scaler_b = StandardScaler().fit(train_b)
    train_a, test_a = scaler_a.transform(train_a), scaler_a.transform(test_a)
    train_b, test_b = scaler_b.transform(train_b), scaler_b.transform(test_b)
    classifier = LogisticRegression(max_iter=2000, random_state=seed).fit(
        np.column_stack([train_a, train_b]), train_y
    )
    complete_accuracy = float(
        accuracy_score(test_y, classifier.predict(np.column_stack([test_a, test_b])))
    )
    predictions, timings, balls = _fit_predictors(train_a, train_b, test_a, seed + 10)
    rows = []
    rng = np.random.default_rng(seed + 20)
    order = rng.permutation(len(test_y))
    for rate in MISSING_RATES:
        missing = np.zeros(len(test_y), dtype=bool)
        missing[order[: int(round(rate * len(test_y)))]] = True
        for method in METHODS:
            recovered = test_b.copy()
            recovered[missing] = predictions[method][missing]
            prediction = classifier.predict(np.column_stack([test_a, recovered]))
            scale = max(float(np.std(test_b[missing])), 1e-9)
            nrmse = float(
                np.sqrt(np.mean((predictions[method][missing] - test_b[missing]) ** 2)) / scale
            )
            class_scores = []
            for label in np.unique(test_y):
                selected = missing & (test_y == label)
                if selected.any():
                    class_scores.append(float(accuracy_score(test_y[selected], prediction[selected])))
            rows.append(
                {
                    "method": method,
                    "missing_rate": rate,
                    "imputation_nrmse": nrmse,
                    "accuracy": float(accuracy_score(test_y, prediction)),
                    "missing_item_accuracy": float(accuracy_score(test_y[missing], prediction[missing])),
                    "worst_class_missing_accuracy": min(class_scores),
                    "accuracy_gap_vs_complete": float(accuracy_score(test_y, prediction) - complete_accuracy),
                    "recovery_seconds": timings[method],
                }
            )
    return {"dataset": dataset, "seed": seed, "complete_accuracy": complete_accuracy, "terminal_balls": balls, "frontier": rows}
