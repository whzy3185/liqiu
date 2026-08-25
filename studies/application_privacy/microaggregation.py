"""Equal-k numerical microaggregation with matched partition baselines."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


DATASETS = ("breast_cancer", "wine", "digits", "covertype")
METHODS = ("granular_ball", "kmeans_merge", "mdav", "axis_tree", "random_groups")
K_VALUES = (5, 10, 20)


def _load(dataset, seed, max_samples=1000):
    if dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "wine":
        bundle = load_wine()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "covertype":
        bundle = fetch_openml(data_id=1596, as_frame=False, parser="auto")
        features, labels = np.asarray(bundle.data, float), LabelEncoder().fit_transform(bundle.target)
    else:
        raise ValueError(dataset)
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    return features, np.asarray(labels, int)


def _gb_groups(features, k, seed):
    groups = [np.arange(len(features))]
    split_round = 0
    blocked = set()
    while True:
        candidates = []
        for position, indices in enumerate(groups):
            if position in blocked or len(indices) < 2 * k:
                continue
            local = features[indices]
            center = local.mean(axis=0)
            candidates.append((float(np.sum((local - center) ** 2)), position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates)
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(features[indices])
        children = [indices[labels == label] for label in (0, 1)]
        if min(map(len, children)) < k:
            blocked.add(position)
            continue
        groups[position : position + 1] = children
        blocked = {value + 1 if value > position else value for value in blocked if value != position}
        split_round += 1
    return groups


def _merge_small(features, groups, k):
    groups = [np.asarray(group) for group in groups if len(group)]
    while any(len(group) < k for group in groups) and len(groups) > 1:
        source = min(range(len(groups)), key=lambda index: len(groups[index]))
        center = features[groups[source]].mean(axis=0)
        targets = [index for index in range(len(groups)) if index != source]
        target = min(
            targets,
            key=lambda index: float(np.linalg.norm(center - features[groups[index]].mean(axis=0))),
        )
        groups[target] = np.concatenate([groups[target], groups[source]])
        groups.pop(source)
    return groups


def _kmeans_groups(features, k, seed):
    count = max(1, len(features) // k)
    labels = KMeans(count, n_init=5, random_state=seed).fit_predict(features)
    return _merge_small(features, [np.flatnonzero(labels == label) for label in range(count)], k)


def _axis_groups(features, k):
    groups = [np.arange(len(features))]
    blocked = set()
    while True:
        candidates = []
        for position, indices in enumerate(groups):
            if position in blocked or len(indices) < 2 * k:
                continue
            variance = np.var(features[indices], axis=0)
            candidates.append((float(variance.max() * len(indices)), position, indices, int(np.argmax(variance))))
        if not candidates:
            break
        _, position, indices, feature = max(candidates)
        ordered = indices[np.argsort(features[indices, feature])]
        middle = len(ordered) // 2
        if middle < k or len(ordered) - middle < k:
            blocked.add(position)
            continue
        groups[position : position + 1] = [ordered[:middle], ordered[middle:]]
        blocked = {value + 1 if value > position else value for value in blocked if value != position}
    return groups


def _mdav_groups(features, k):
    remaining = list(range(len(features)))
    groups = []
    while len(remaining) >= 2 * k:
        local = features[remaining]
        centroid = local.mean(axis=0)
        first = remaining[int(np.argmax(np.linalg.norm(local - centroid, axis=1)))]
        second = remaining[int(np.argmax(np.linalg.norm(local - features[first], axis=1)))]
        for anchor in (first, second):
            if len(remaining) < k:
                break
            ordered = sorted(remaining, key=lambda item: float(np.linalg.norm(features[item] - features[anchor])))
            group = ordered[:k]
            groups.append(np.asarray(group))
            selected = set(group)
            remaining = [item for item in remaining if item not in selected]
    if remaining:
        if not groups:
            groups.append(np.asarray(remaining))
        else:
            for item in remaining:
                target = min(
                    range(len(groups)),
                    key=lambda index: float(
                        np.linalg.norm(features[item] - features[groups[index]].mean(axis=0))
                    ),
                )
                groups[target] = np.append(groups[target], item)
    return groups


def _random_groups(features, k, seed):
    ordered = np.random.default_rng(seed).permutation(len(features))
    count = max(1, len(features) // k)
    return _merge_small(features, np.array_split(ordered, count), k)


def _anonymize(features, groups):
    output = features.copy()
    for group in groups:
        output[group] = features[group].mean(axis=0)
    return output


def _downstream(train_x, train_y, test_x, test_y, seed):
    model = LogisticRegression(max_iter=2000, random_state=seed).fit(train_x, train_y)
    return float(balanced_accuracy_score(test_y, model.predict(test_x)))


def evaluate_microaggregation(dataset: str, seed: int):
    features, labels = _load(dataset, seed)
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    scaler = StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)
    clean_accuracy = _downstream(train_x, train_y, test_x, test_y, seed)
    rows = []
    for k in K_VALUES:
        for method in METHODS:
            start = time.perf_counter()
            if method == "granular_ball":
                groups = _gb_groups(train_x, k, seed + k)
            elif method == "kmeans_merge":
                groups = _kmeans_groups(train_x, k, seed + k)
            elif method == "mdav":
                groups = _mdav_groups(train_x, k)
            elif method == "axis_tree":
                groups = _axis_groups(train_x, k)
            elif method == "random_groups":
                groups = _random_groups(train_x, k, seed + k)
            else:
                raise ValueError(method)
            anonymized = _anonymize(train_x, groups)
            runtime = time.perf_counter() - start
            distortion = float(np.mean((anonymized - train_x) ** 2))
            accuracy = _downstream(anonymized, train_y, test_x, test_y, seed)
            rows.append(
                {
                    "method": method,
                    "k": k,
                    "groups": len(groups),
                    "minimum_group_size": min(map(len, groups)),
                    "maximum_group_size": max(map(len, groups)),
                    "distortion_mse": distortion,
                    "downstream_accuracy": accuracy,
                    "accuracy_delta_vs_clean": accuracy - clean_accuracy,
                    "runtime_seconds": runtime,
                }
            )
    return {"dataset": dataset, "seed": seed, "train_items": len(train_y), "clean_accuracy": clean_accuracy, "frontier": rows}
