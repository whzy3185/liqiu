"""Equal-point-budget point-cloud compression for shape retrieval."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


REGIMES = ("uniform", "density_bias", "outliers", "occlusion")
METHODS = ("granular_ball", "kmeans", "fps", "axis_cells", "random", "full")
BUDGETS = (32, 64, 128)
SHAPES = ("sphere", "cube", "cylinder", "torus", "cone")


def _sample_shape(kind: str, rng: np.random.Generator, count: int) -> np.ndarray:
    if kind == "sphere":
        points = rng.normal(size=(count, 3))
        points /= np.linalg.norm(points, axis=1, keepdims=True)
    elif kind == "cube":
        points = rng.uniform(-1, 1, size=(count, 3))
        faces = rng.integers(3, size=count)
        signs = rng.choice([-1.0, 1.0], size=count)
        points[np.arange(count), faces] = signs
    elif kind == "cylinder":
        angle = rng.uniform(0, 2 * np.pi, size=count)
        z = rng.uniform(-1, 1, size=count)
        points = np.column_stack([np.cos(angle), np.sin(angle), z])
    elif kind == "torus":
        major = rng.uniform(0, 2 * np.pi, size=count)
        minor = rng.uniform(0, 2 * np.pi, size=count)
        radius = 0.35
        points = np.column_stack(
            [
                (1 + radius * np.cos(minor)) * np.cos(major),
                (1 + radius * np.cos(minor)) * np.sin(major),
                radius * np.sin(minor),
            ]
        )
    elif kind == "cone":
        z = rng.uniform(-1, 1, size=count)
        angle = rng.uniform(0, 2 * np.pi, size=count)
        radius = (1 - z) / 2
        points = np.column_stack([radius * np.cos(angle), radius * np.sin(angle), z])
    else:
        raise ValueError(kind)
    angle = rng.uniform(-0.35, 0.35)
    rotation = np.array(
        [[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]]
    )
    points = points @ rotation.T
    points *= rng.uniform(0.85, 1.15)
    points += rng.normal(0, 0.015, size=points.shape)
    return points


def _apply_regime(points: np.ndarray, regime: str, rng: np.random.Generator, count: int):
    if regime == "uniform":
        selected = rng.choice(len(points), count, replace=False)
        output = points[selected]
    elif regime == "density_bias":
        probability = np.exp(2.5 * points[:, 0])
        probability /= probability.sum()
        output = points[rng.choice(len(points), count, replace=True, p=probability)]
    elif regime == "outliers":
        selected = rng.choice(len(points), count, replace=False)
        output = points[selected]
        outliers = rng.choice(count, max(1, count // 10), replace=False)
        output[outliers] = rng.uniform(-1.7, 1.7, size=(len(outliers), 3))
    elif regime == "occlusion":
        visible = points[points[:, 0] >= np.quantile(points[:, 0], 0.25)]
        output = visible[rng.choice(len(visible), count, replace=len(visible) < count)]
    else:
        raise ValueError(regime)
    return output - output.mean(axis=0)


def generate_dataset(regime: str, seed: int, objects_per_class: int = 10, points: int = 256):
    rng = np.random.default_rng(seed)
    clouds = []
    labels = []
    for label, shape in enumerate(SHAPES):
        for _ in range(objects_per_class):
            raw = _sample_shape(shape, rng, points * 4)
            clouds.append(_apply_regime(raw, regime, rng, points))
            labels.append(label)
    return np.asarray(clouds), np.asarray(labels)


def _gb_compress(points, count, seed):
    groups = [np.arange(len(points))]
    split_round = 0
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            local = points[indices]
            center = local.mean(axis=0)
            score = len(indices) * float(np.median(np.linalg.norm(local - center, axis=1)))
            candidates.append((score, position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates)
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(points[indices])
        children = [indices[labels == label] for label in (0, 1)]
        if min(map(len, children)) == 0:
            break
        groups[position : position + 1] = children
        split_round += 1
    centers = np.vstack([points[indices].mean(axis=0) for indices in groups[:count]])
    weights = np.asarray([len(indices) for indices in groups[:count]], float)
    weights /= weights.sum()
    return centers, weights


def _kmeans_compress(points, count, seed):
    model = KMeans(count, n_init=3, max_iter=100, random_state=seed).fit(points)
    weights = np.bincount(model.labels_, minlength=count).astype(float)
    weights /= weights.sum()
    return model.cluster_centers_, weights


def _fps(points, count, seed):
    selected = [int(np.random.default_rng(seed).integers(len(points)))]
    distance = np.linalg.norm(points - points[selected[0]], axis=1)
    for _ in range(1, count):
        choice = int(np.argmax(distance))
        selected.append(choice)
        distance = np.minimum(distance, np.linalg.norm(points - points[choice], axis=1))
        distance[selected] = -1
    return points[selected], np.full(count, 1 / count)


def _axis_compress(points, count):
    groups = [np.arange(len(points))]
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            variance = np.var(points[indices], axis=0)
            candidates.append((float(variance.max() * len(indices)), position, indices, int(np.argmax(variance))))
        if not candidates:
            break
        _, position, indices, feature = max(candidates)
        ordered = indices[np.argsort(points[indices, feature])]
        middle = len(ordered) // 2
        groups[position : position + 1] = [ordered[:middle], ordered[middle:]]
    centers = np.vstack([points[indices].mean(axis=0) for indices in groups[:count]])
    weights = np.asarray([len(indices) for indices in groups[:count]], float)
    weights /= weights.sum()
    return centers, weights


def _descriptor(points, weights):
    centered = points - np.average(points, axis=0, weights=weights)
    covariance = (centered * weights[:, None]).T @ centered
    eigenvalues = np.sort(np.linalg.eigvalsh(covariance))[::-1]
    radius = np.linalg.norm(centered, axis=1)
    maximum = max(float(radius.max()), 1e-9)
    radial, _ = np.histogram(radius, bins=10, range=(0, maximum), weights=weights)
    pairwise = np.linalg.norm(centered[:, None, :] - centered[None, :, :], axis=2)
    pair_weights = weights[:, None] * weights[None, :]
    distance_hist, _ = np.histogram(
        pairwise.ravel(), bins=12, range=(0, max(float(pairwise.max()), 1e-9)), weights=pair_weights.ravel()
    )
    axis_hist = []
    for feature in range(3):
        values, _ = np.histogram(
            centered[:, feature], bins=6, range=(-maximum, maximum), weights=weights
        )
        axis_hist.extend(values)
    return np.concatenate([eigenvalues, radial, distance_hist, axis_hist])


def _chamfer(original, centers):
    distances = np.linalg.norm(original[:, None, :] - centers[None, :, :], axis=2)
    return float(distances.min(axis=1).mean() + distances.min(axis=0).mean())


def _retrieval(descriptors, labels, gallery_ids, query_ids, k=10):
    scaler = StandardScaler().fit(descriptors[gallery_ids])
    gallery = scaler.transform(descriptors[gallery_ids])
    query = scaler.transform(descriptors[query_ids])
    distances = np.linalg.norm(query[:, None, :] - gallery[None, :, :], axis=2)
    top = np.argsort(distances, axis=1)[:, :k]
    relevance = labels[gallery_ids][top] == labels[query_ids, None]
    precision = np.cumsum(relevance, axis=1) / np.arange(1, k + 1)
    denominators = np.minimum(np.bincount(labels[gallery_ids])[labels[query_ids]], k)
    ap = np.sum(precision * relevance, axis=1) / np.maximum(denominators, 1)
    prediction = np.asarray(
        [np.bincount(labels[gallery_ids][row], minlength=len(SHAPES)).argmax() for row in top]
    )
    return float(ap.mean()), float(accuracy_score(labels[query_ids], prediction))


def evaluate_pointcloud_compression(regime: str, seed: int):
    clouds, labels = generate_dataset(regime, seed)
    gallery_ids, query_ids = train_test_split(
        np.arange(len(labels)), test_size=0.35, stratify=labels, random_state=seed
    )
    rows = []
    for budget in BUDGETS:
        method_descriptors = {method: [] for method in METHODS}
        method_chamfer = {method: [] for method in METHODS}
        method_seconds = {method: 0.0 for method in METHODS}
        for object_id, points in enumerate(clouds):
            for method in METHODS:
                start = time.perf_counter()
                if method == "granular_ball":
                    centers, weights = _gb_compress(points, budget, seed + object_id + budget)
                elif method == "kmeans":
                    centers, weights = _kmeans_compress(points, budget, seed + object_id + budget)
                elif method == "fps":
                    centers, weights = _fps(points, budget, seed + object_id + budget)
                elif method == "axis_cells":
                    centers, weights = _axis_compress(points, budget)
                elif method == "random":
                    chosen = np.random.default_rng(seed + object_id + budget).choice(
                        len(points), budget, replace=False
                    )
                    centers, weights = points[chosen], np.full(budget, 1 / budget)
                elif method == "full":
                    centers, weights = points, np.full(len(points), 1 / len(points))
                else:
                    raise ValueError(method)
                method_seconds[method] += time.perf_counter() - start
                method_descriptors[method].append(_descriptor(centers, weights))
                method_chamfer[method].append(_chamfer(points, centers))
        for method in METHODS:
            descriptors = np.asarray(method_descriptors[method])
            map_at_10, accuracy = _retrieval(descriptors, labels, gallery_ids, query_ids)
            rows.append(
                {
                    "method": method,
                    "budget": budget if method != "full" else len(clouds[0]),
                    "map_at_10": map_at_10,
                    "knn_accuracy": accuracy,
                    "mean_chamfer": float(np.mean(method_chamfer[method])),
                    "compression_seconds": method_seconds[method],
                }
            )
    return {"regime": regime, "seed": seed, "objects": len(clouds), "points": len(clouds[0]), "frontier": rows}
