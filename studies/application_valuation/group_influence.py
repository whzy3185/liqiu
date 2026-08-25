"""Approximate leave-one-out data influence through matched group partitions."""

from __future__ import annotations

import time

import numpy as np
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.datasets import load_breast_cancer, load_digits, load_wine, make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from studies.risk_granularity.tree import GranulationTree


DATASETS = ("breast_cancer", "wine", "digits", "moons")
METHODS = ("granular_ball", "kmeans", "decision_tree", "random_groups")


def _load(dataset: str, seed: int, max_samples: int = 320):
    if dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "wine":
        bundle = load_wine()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "moons":
        features, labels = make_moons(n_samples=max_samples, noise=0.25, random_state=seed)
    else:
        raise ValueError(dataset)
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    return features, np.asarray(labels, int)


def _model(seed):
    return LogisticRegression(max_iter=2000, random_state=seed)


def _loss(train_x, train_y, validation_x, validation_y, classes, seed):
    probabilities = _model(seed).fit(train_x, train_y).predict_proba(validation_x)
    full = np.zeros((len(validation_x), len(classes)))
    trained_classes = np.unique(train_y)
    full[:, trained_classes] = probabilities
    full = np.clip(full, 1e-12, 1)
    full /= full.sum(axis=1, keepdims=True)
    return float(log_loss(validation_y, full, labels=classes))


def _exact_influence(train_x, train_y, validation_x, validation_y, seed):
    classes = np.arange(len(np.unique(np.concatenate([train_y, validation_y]))))
    baseline = _loss(train_x, train_y, validation_x, validation_y, classes, seed)
    scores = np.empty(len(train_y))
    start = time.perf_counter()
    for item in range(len(train_y)):
        keep = np.arange(len(train_y)) != item
        if len(np.unique(train_y[keep])) < len(classes):
            scores[item] = -np.inf
        else:
            scores[item] = baseline - _loss(
                train_x[keep], train_y[keep], validation_x, validation_y, classes, seed + item + 1
            )
    return scores, time.perf_counter() - start, baseline


def _gb_groups(train_x, train_y, seed):
    tree = GranulationTree(random_state=seed, split_method="kmeans").fit(train_x, train_y)
    leaves = None
    selected_tau = None
    for tau in (0.85, 0.80, 0.70, 0.60):
        candidate = tree.cut(tau)
        if len(candidate) <= 40:
            leaves, selected_tau = candidate, tau
            break
    if leaves is None:
        leaves, selected_tau = tree.cut(0.60), 0.60
    return [leaf.indices for leaf in leaves], selected_tau


def _partition_groups(method, train_x, train_y, count, seed):
    if method == "kmeans":
        labels = KMeans(count, n_init=10, random_state=seed).fit_predict(train_x)
        return [np.flatnonzero(labels == label) for label in range(count)]
    if method == "decision_tree":
        model = DecisionTreeClassifier(
            max_leaf_nodes=count, min_samples_leaf=2, random_state=seed
        ).fit(train_x, train_y)
        leaf = model.apply(train_x)
        return [np.flatnonzero(leaf == value) for value in np.unique(leaf)]
    if method == "random_groups":
        ordered = np.random.default_rng(seed).permutation(len(train_y))
        return [group for group in np.array_split(ordered, count) if len(group)]
    raise ValueError(method)


def _group_influence(groups, train_x, train_y, validation_x, validation_y, baseline, seed):
    classes = np.arange(len(np.unique(np.concatenate([train_y, validation_y]))))
    scores = np.zeros(len(train_y))
    start = time.perf_counter()
    valid_groups = 0
    for group_id, group in enumerate(groups):
        keep = np.ones(len(train_y), dtype=bool)
        keep[group] = False
        if len(np.unique(train_y[keep])) < len(classes):
            continue
        effect = baseline - _loss(
            train_x[keep], train_y[keep], validation_x, validation_y, classes, seed + group_id + 1
        )
        scores[group] = effect / len(group)
        valid_groups += 1
    return scores, time.perf_counter() - start, valid_groups


def _metrics(approximation, exact, noise_mask, runtime, retrains):
    finite = np.isfinite(exact)
    correlation = spearmanr(exact[finite], approximation[finite]).statistic
    correlation = float(correlation) if np.isfinite(correlation) else 0.0
    top_count = max(1, int(np.ceil(0.10 * finite.sum())))
    finite_ids = np.flatnonzero(finite)
    exact_top = set(finite_ids[np.argsort(-exact[finite])[:top_count]])
    approximate_top = set(finite_ids[np.argsort(-approximation[finite])[:top_count]])
    return {
        "spearman_exact_influence": correlation,
        "top_harmful_overlap": len(exact_top & approximate_top) / top_count,
        "noise_auprc": float(average_precision_score(noise_mask, approximation)),
        "runtime_seconds": runtime,
        "retrains": retrains,
    }


def evaluate_group_influence(dataset: str, seed: int):
    features, labels = _load(dataset, seed)
    train_x, holdout_x, train_y, holdout_y = train_test_split(
        features, labels, test_size=0.40, stratify=labels, random_state=seed
    )
    validation_x, test_x, validation_y, test_y = train_test_split(
        holdout_x, holdout_y, test_size=0.50, stratify=holdout_y, random_state=seed + 1
    )
    scaler = StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x)
    validation_x = scaler.transform(validation_x)
    test_x = scaler.transform(test_x)
    rng = np.random.default_rng(seed + 10)
    noise_mask = np.zeros(len(train_y), dtype=bool)
    noise_ids = rng.choice(len(train_y), max(1, int(round(0.10 * len(train_y)))), replace=False)
    noise_mask[noise_ids] = True
    noisy_y = train_y.copy()
    classes = len(np.unique(labels))
    for item in noise_ids:
        wrong = rng.integers(classes - 1)
        noisy_y[item] = wrong + (wrong >= noisy_y[item])
    exact, exact_seconds, baseline = _exact_influence(
        train_x, noisy_y, validation_x, validation_y, seed
    )
    gb_groups, tau = _gb_groups(train_x, noisy_y, seed + 20)
    count = max(2, len(gb_groups))
    rows = []
    for method in METHODS:
        groups = gb_groups if method == "granular_ball" else _partition_groups(
            method, train_x, noisy_y, count, seed + 30
        )
        scores, runtime, retrains = _group_influence(
            groups, train_x, noisy_y, validation_x, validation_y, baseline, seed + 40
        )
        rows.append(
            {
                "method": method,
                "groups": len(groups),
                "selected_tau": tau if method == "granular_ball" else None,
                **_metrics(scores, exact, noise_mask, runtime, retrains),
            }
        )
    clean_test_loss = _loss(train_x, noisy_y, test_x, test_y, np.arange(classes), seed + 99)
    return {
        "dataset": dataset,
        "seed": seed,
        "train_items": len(train_y),
        "noise_rate": float(noise_mask.mean()),
        "exact_runtime_seconds": exact_seconds,
        "exact_retrains": len(train_y),
        "noisy_test_loss": clean_test_loss,
        "methods": rows,
    }
