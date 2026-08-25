"""Fixed-budget sensor placement over heterogeneous spatial fields."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


FAMILIES = ("smooth_multiscale", "anisotropic", "discontinuous", "local_hotspots")
METHODS = ("granular_ball", "kmeans", "kcenter", "facility_location", "axis_tree", "random")
BUDGETS = (0.05, 0.10, 0.20)


def _coordinates(rng: np.random.Generator, count: int) -> np.ndarray:
    clustered = rng.random(count) < 0.65
    points = rng.uniform(0, 1, size=(count, 2))
    points[clustered] = np.clip(
        rng.normal(loc=np.array([0.32, 0.38]), scale=np.array([0.16, 0.12]), size=(clustered.sum(), 2)),
        0,
        1,
    )
    return points


def _basis(family: str, coordinates: np.ndarray, rng: np.random.Generator):
    x, y = coordinates[:, 0], coordinates[:, 1]
    if family == "smooth_multiscale":
        centers = rng.uniform(0.05, 0.95, size=(8, 2))
        scales = np.array([0.08, 0.10, 0.14, 0.18, 0.24, 0.30, 0.38, 0.48])
        values = [
            np.exp(-np.sum((coordinates - center) ** 2, axis=1) / (2 * scale**2))
            for center, scale in zip(centers, scales)
        ]
        basis = np.column_stack(values)
        regions = np.argmax(basis[:, :4], axis=1)
    elif family == "anisotropic":
        basis = np.column_stack(
            [
                np.sin(2 * np.pi * x),
                np.cos(2 * np.pi * y),
                np.sin(3 * np.pi * (0.85 * x + 0.20 * y)),
                np.cos(4 * np.pi * (0.15 * x + 0.90 * y)),
                np.exp(-((x - 0.65) ** 2 / 0.02 + (y - 0.35) ** 2 / 0.20)),
                np.exp(-((x - 0.25) ** 2 / 0.18 + (y - 0.75) ** 2 / 0.015)),
            ]
        )
        regions = (x > 0.5).astype(int) + 2 * (y > 0.5).astype(int)
    elif family == "discontinuous":
        regions = (x > 0.48).astype(int) + 2 * (y > 0.55).astype(int)
        zone = np.eye(4)[regions]
        basis = np.column_stack(
            [zone, np.sin(2 * np.pi * x), np.cos(2 * np.pi * y), x * y]
        )
    elif family == "local_hotspots":
        centers = rng.uniform(0.05, 0.95, size=(10, 2))
        scales = rng.uniform(0.025, 0.10, size=10)
        basis = np.column_stack(
            [
                np.exp(-np.sum((coordinates - center) ** 2, axis=1) / (2 * scale**2))
                for center, scale in zip(centers, scales)
            ]
        )
        regions = np.argmax(basis[:, :4], axis=1)
    else:
        raise ValueError(family)
    basis = StandardScaler().fit_transform(basis)
    return basis, regions


def generate_field(family: str, seed: int, sites: int = 400, history: int = 48, future: int = 24):
    rng = np.random.default_rng(seed)
    coordinates = _coordinates(rng, sites)
    basis, regions = _basis(family, coordinates, rng)
    total = history + future
    coefficients = np.zeros((basis.shape[1], total))
    coefficients[:, 0] = rng.normal(size=basis.shape[1])
    for step in range(1, total):
        coefficients[:, step] = 0.82 * coefficients[:, step - 1] + rng.normal(
            0, 0.55, size=basis.shape[1]
        )
    signal = basis @ coefficients + rng.normal(0, 0.08, size=(sites, total))
    return coordinates, signal[:, :history], signal[:, history:], regions


def _selection_features(coordinates: np.ndarray, history: np.ndarray) -> np.ndarray:
    components = PCA(n_components=min(5, history.shape[1]), random_state=0).fit_transform(history)
    return StandardScaler().fit_transform(np.column_stack([coordinates, components]))


def _medoid(features: np.ndarray, indices: np.ndarray) -> int:
    center = features[indices].mean(axis=0)
    return int(indices[np.argmin(np.linalg.norm(features[indices] - center, axis=1))])


def _gb_select(features: np.ndarray, count: int, seed: int) -> np.ndarray:
    groups = [np.arange(len(features))]
    split_round = 0
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            local = features[indices]
            center = local.mean(axis=0)
            score = len(indices) * float(np.median(np.linalg.norm(local - center, axis=1)))
            candidates.append((score, position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates)
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(features[indices])
        children = [indices[labels == label] for label in (0, 1)]
        if min(map(len, children)) == 0:
            break
        groups[position : position + 1] = children
        split_round += 1
    selected = [_medoid(features, indices) for indices in groups]
    if len(selected) < count:
        remaining = np.setdiff1d(np.arange(len(features)), selected)
        selected.extend(map(int, remaining[: count - len(selected)]))
    return np.asarray(selected[:count])


def _kmeans_select(features: np.ndarray, count: int, seed: int) -> np.ndarray:
    labels = KMeans(count, n_init=10, random_state=seed).fit_predict(features)
    return np.asarray([_medoid(features, np.flatnonzero(labels == label)) for label in range(count)])


def _kcenter_order(features: np.ndarray, count: int, seed: int) -> np.ndarray:
    first = int(np.random.default_rng(seed).integers(len(features)))
    selected = [first]
    distance = np.linalg.norm(features - features[first], axis=1)
    for _ in range(1, count):
        choice = int(np.argmax(distance))
        selected.append(choice)
        distance = np.minimum(distance, np.linalg.norm(features - features[choice], axis=1))
        distance[selected] = -1
    return np.asarray(selected)


def _facility_order(features: np.ndarray, count: int) -> np.ndarray:
    squared = np.maximum(
        np.sum(features * features, axis=1)[:, None]
        + np.sum(features * features, axis=1)[None, :]
        - 2 * features @ features.T,
        0,
    )
    positive = squared[squared > 1e-12]
    scale = float(np.median(positive)) if len(positive) else 1.0
    similarity = np.exp(-squared / max(scale, 1e-12))
    coverage = np.zeros(len(features))
    selected = []
    available = np.ones(len(features), dtype=bool)
    for _ in range(count):
        gains = np.sum(np.maximum(similarity - coverage[:, None], 0), axis=0)
        gains[~available] = -np.inf
        choice = int(np.argmax(gains))
        selected.append(choice)
        available[choice] = False
        coverage = np.maximum(coverage, similarity[:, choice])
    return np.asarray(selected)


def _axis_select(features: np.ndarray, count: int) -> np.ndarray:
    groups = [np.arange(len(features))]
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            variances = np.var(features[indices], axis=0)
            candidates.append((float(variances.max() * len(indices)), position, indices, int(np.argmax(variances))))
        if not candidates:
            break
        _, position, indices, feature = max(candidates)
        order = indices[np.argsort(features[indices, feature])]
        middle = len(order) // 2
        groups[position : position + 1] = [order[:middle], order[middle:]]
    return np.asarray([_medoid(features, indices) for indices in groups[:count]])


def _reconstruction(selected, history, future, regions):
    unselected = np.setdiff1d(np.arange(len(history)), selected)
    model = Ridge(alpha=1.0).fit(history[selected].T, history[unselected].T)
    prediction = model.predict(future[selected].T).T
    truth = future[unselected]
    scale = max(float(np.std(truth)), 1e-9)
    normalized_rmse = float(np.sqrt(np.mean((prediction - truth) ** 2)) / scale)
    normalized_mae = float(np.mean(np.abs(prediction - truth)) / scale)
    region_rmse = []
    for region in np.unique(regions):
        local = regions[unselected] == region
        if local.any():
            region_rmse.append(float(np.sqrt(np.mean((prediction[local] - truth[local]) ** 2)) / scale))
    return normalized_rmse, normalized_mae, max(region_rmse)


def evaluate_sensor_placement(family: str, seed: int):
    coordinates, history, future, regions = generate_field(family, seed)
    features = _selection_features(coordinates, history)
    maximum = int(np.ceil(max(BUDGETS) * len(features)))
    start = time.perf_counter()
    kcenter = _kcenter_order(features, maximum, seed + 10)
    kcenter_seconds = time.perf_counter() - start
    start = time.perf_counter()
    facility = _facility_order(features, maximum)
    facility_seconds = time.perf_counter() - start
    random_order = np.random.default_rng(seed + 20).permutation(len(features))[:maximum]
    rows = []
    for fraction in BUDGETS:
        count = int(np.ceil(fraction * len(features)))
        selections = {}
        timings = {}
        for method, selector in (
            ("granular_ball", lambda: _gb_select(features, count, seed + count)),
            ("kmeans", lambda: _kmeans_select(features, count, seed + count)),
            ("axis_tree", lambda: _axis_select(features, count)),
        ):
            start = time.perf_counter()
            selections[method] = selector()
            timings[method] = time.perf_counter() - start
        selections["kcenter"] = kcenter[:count]
        selections["facility_location"] = facility[:count]
        selections["random"] = random_order[:count]
        timings["kcenter"] = kcenter_seconds * count / maximum
        timings["facility_location"] = facility_seconds * count / maximum
        timings["random"] = 0.0
        for method in METHODS:
            rmse, mae, worst = _reconstruction(
                selections[method], history, future, regions
            )
            nearest = np.linalg.norm(
                coordinates[:, None, :] - coordinates[selections[method]][None, :, :], axis=2
            ).min(axis=1)
            rows.append(
                {
                    "method": method,
                    "fraction": fraction,
                    "sensors": count,
                    "normalized_rmse": rmse,
                    "normalized_mae": mae,
                    "worst_region_rmse": worst,
                    "mean_spatial_coverage_distance": float(nearest.mean()),
                    "selection_seconds": timings[method],
                }
            )
    return {"family": family, "seed": seed, "sites": len(features), "frontier": rows}
