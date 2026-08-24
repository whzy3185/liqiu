"""Fixed-memory distribution sketches for granular-ball application tests."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler


SHIFT_KINDS = ("translation", "local_emergence", "variance", "mixture_weight")


def _squared_distances(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.maximum(
        np.sum(left * left, axis=1)[:, None]
        + np.sum(right * right, axis=1)[None, :]
        - 2 * left @ right.T,
        0.0,
    )


def _median_gamma(points: np.ndarray) -> float:
    sample = points[: min(300, len(points))]
    distances = _squared_distances(sample, sample)
    positive = distances[distances > 1e-12]
    median = float(np.median(positive)) if len(positive) else 1.0
    return 1.0 / max(median, 1e-12)


def _mmd(reference: np.ndarray, batch: np.ndarray, gamma: float) -> float:
    kxx = np.exp(-gamma * _squared_distances(reference, reference)).mean()
    kyy = np.exp(-gamma * _squared_distances(batch, batch)).mean()
    kxy = np.exp(-gamma * _squared_distances(reference, batch)).mean()
    return float(max(kxx + kyy - 2 * kxy, 0.0))


@dataclass(frozen=True)
class BallSketch:
    centers: np.ndarray
    radii: np.ndarray
    weights: np.ndarray

    @property
    def memory_bytes(self) -> int:
        return int((self.centers.size + self.radii.size + self.weights.size) * 8)

    def score(self, batch: np.ndarray) -> float:
        distances = np.sqrt(_squared_distances(batch, self.centers))
        surface = distances - self.radii[None, :]
        assigned = np.argmin(surface, axis=1)
        chosen_distance = distances[np.arange(len(batch)), assigned]
        chosen_radius = self.radii[assigned]
        excess = np.maximum((chosen_distance - chosen_radius) / chosen_radius, 0.0)
        occupancy = np.bincount(assigned, minlength=len(self.weights)) / len(batch)
        occupancy_tv = 0.5 * np.abs(occupancy - self.weights).sum()
        return float(excess.mean() + 0.5 * occupancy_tv)


def _make_sketch(points: np.ndarray, groups: list[np.ndarray]) -> BallSketch:
    centers = []
    radii = []
    weights = []
    for indices in groups:
        local = points[indices]
        center = local.mean(axis=0)
        distances = np.linalg.norm(local - center, axis=1)
        centers.append(center)
        radii.append(max(float(np.quantile(distances, 0.95)), 1e-6))
        weights.append(len(indices) / len(points))
    return BallSketch(np.vstack(centers), np.asarray(radii), np.asarray(weights))


def fit_granular_ball_sketch(points: np.ndarray, budget: int, seed: int) -> BallSketch:
    """Bisect the highest-dispersion ball until the memory budget is filled."""

    groups = [np.arange(len(points))]
    split_round = 0
    while len(groups) < budget:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 4:
                continue
            local = points[indices]
            center = local.mean(axis=0)
            sse = float(np.sum((local - center) ** 2))
            candidates.append((sse, position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates, key=lambda row: row[0])
        labels = KMeans(
            2, n_init=5, random_state=seed + split_round
        ).fit_predict(points[indices])
        left = indices[labels == 0]
        right = indices[labels == 1]
        if len(left) == 0 or len(right) == 0:
            break
        groups[position : position + 1] = [left, right]
        split_round += 1
    return _make_sketch(points, groups)


def fit_kmeans_sketch(points: np.ndarray, budget: int, seed: int) -> BallSketch:
    labels = KMeans(budget, n_init=10, random_state=seed).fit_predict(points)
    groups = [np.flatnonzero(labels == label) for label in range(budget)]
    return _make_sketch(points, groups)


def _sample_mixture(
    rng: np.random.Generator,
    count: int,
    dimension: int,
    shift_kind: str,
    severity: float,
) -> np.ndarray:
    if shift_kind not in SHIFT_KINDS:
        raise ValueError(shift_kind)
    weights = np.array([0.40, 0.35, 0.25])
    if shift_kind == "mixture_weight":
        weights = (1 - severity) * weights + severity * np.array([0.80, 0.15, 0.05])
    labels = rng.choice(3, size=count, p=weights)
    means = np.array([[-2.0, 0.0], [0.0, 1.8], [2.0, 0.0]])
    informative = means[labels] + rng.normal(0, 0.35, size=(count, 2))
    if shift_kind == "translation":
        informative[:, 0] += 1.5 * severity
    elif shift_kind == "variance":
        mask = labels == 1
        informative[mask] = means[1] + (informative[mask] - means[1]) * (1 + 3 * severity)
    elif shift_kind == "local_emergence" and severity > 0:
        emerging = rng.random(count) < 0.40 * severity
        informative[emerging] = np.array([0.0, -2.5]) + rng.normal(
            0, 0.30, size=(emerging.sum(), 2)
        )
    if dimension == 2:
        return informative
    nuisance = rng.normal(0, 0.30, size=(count, dimension - 2))
    return np.column_stack([informative, nuisance])


def _calibrated_metrics(
    calibration_scores: list[float],
    null_scores: list[float],
    shifted_scores: dict[float, list[float]],
) -> dict[str, object]:
    threshold = float(np.quantile(calibration_scores, 0.95, method="higher"))
    labels = [0] * len(null_scores)
    scores = list(null_scores)
    detection_rates = {}
    for severity, values in shifted_scores.items():
        labels.extend([1] * len(values))
        scores.extend(values)
        detection_rates[str(severity)] = float(np.mean(np.asarray(values) > threshold))
    first_80 = next(
        (float(level) for level, rate in detection_rates.items() if rate >= 0.80), None
    )
    return {
        "auroc": float(roc_auc_score(labels, scores)),
        "false_positive_rate": float(np.mean(np.asarray(null_scores) > threshold)),
        "threshold": threshold,
        "detection_rates": detection_rates,
        "first_80_detection_severity": first_80,
    }


def evaluate_drift_sketches(
    shift_kind: str,
    seed: int,
    dimension: int = 6,
    reference_size: int = 1200,
    batch_size: int = 200,
    budgets: tuple[int, ...] = (8, 16, 32),
    severities: tuple[float, ...] = (0.2, 0.4, 0.6, 0.8, 1.0),
    calibration_batches: int = 20,
    repeats: int = 10,
) -> list[dict[str, object]]:
    rng = np.random.default_rng(seed)
    reference = _sample_mixture(rng, reference_size, dimension, shift_kind, 0.0)
    scaler = StandardScaler().fit(reference)
    reference = scaler.transform(reference)

    def batch(level: float) -> np.ndarray:
        return scaler.transform(
            _sample_mixture(rng, batch_size, dimension, shift_kind, level)
        )

    calibration = [batch(0.0) for _ in range(calibration_batches)]
    null = [batch(0.0) for _ in range(repeats)]
    shifted = {level: [batch(level) for _ in range(repeats)] for level in severities}
    rows = []

    for budget in budgets:
        for method, fitter in (
            ("granular_ball", fit_granular_ball_sketch),
            ("kmeans", fit_kmeans_sketch),
        ):
            start = time.perf_counter()
            sketch = fitter(reference, budget, seed)
            fit_seconds = time.perf_counter() - start
            start = time.perf_counter()
            calibration_scores = [sketch.score(values) for values in calibration]
            null_scores = [sketch.score(values) for values in null]
            shifted_scores = {
                level: [sketch.score(values) for values in batches]
                for level, batches in shifted.items()
            }
            query_seconds = time.perf_counter() - start
            rows.append(
                {
                    "method": method,
                    "budget": budget,
                    "memory_bytes": sketch.memory_bytes,
                    "fit_seconds": fit_seconds,
                    "mean_query_seconds": query_seconds
                    / (len(calibration) + len(null) + sum(map(len, shifted.values()))),
                    **_calibrated_metrics(calibration_scores, null_scores, shifted_scores),
                }
            )

        reservoir_count = max(2, budget * (dimension + 2) // dimension)
        indices = rng.choice(len(reference), reservoir_count, replace=False)
        reservoir = reference[indices]
        gamma = _median_gamma(reservoir)
        start = time.perf_counter()
        calibration_scores = [_mmd(reservoir, values, gamma) for values in calibration]
        null_scores = [_mmd(reservoir, values, gamma) for values in null]
        shifted_scores = {
            level: [_mmd(reservoir, values, gamma) for values in batches]
            for level, batches in shifted.items()
        }
        query_seconds = time.perf_counter() - start
        rows.append(
            {
                "method": "reservoir_mmd",
                "budget": budget,
                "memory_bytes": int(reservoir.size * 8),
                "fit_seconds": 0.0,
                "mean_query_seconds": query_seconds
                / (len(calibration) + len(null) + sum(map(len, shifted.values()))),
                **_calibrated_metrics(calibration_scores, null_scores, shifted_scores),
            }
        )

    full_reference = reference[: min(600, len(reference))]
    gamma = _median_gamma(full_reference)
    start = time.perf_counter()
    calibration_scores = [_mmd(full_reference, values, gamma) for values in calibration]
    null_scores = [_mmd(full_reference, values, gamma) for values in null]
    shifted_scores = {
        level: [_mmd(full_reference, values, gamma) for values in batches]
        for level, batches in shifted.items()
    }
    query_seconds = time.perf_counter() - start
    rows.append(
        {
            "method": "full_mmd",
            "budget": len(full_reference),
            "memory_bytes": int(full_reference.size * 8),
            "fit_seconds": 0.0,
            "mean_query_seconds": query_seconds
            / (len(calibration) + len(null) + sum(map(len, shifted.values()))),
            **_calibrated_metrics(calibration_scores, null_scores, shifted_scores),
        }
    )
    return rows
