"""Parameterized geometry/noise generators for failure-region search."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
from sklearn.datasets import make_blobs, make_circles, make_moons


FAMILIES = (
    "gaussian_blobs", "moons", "circles", "xor", "checkerboard", "spirals",
    "thin_manifold", "nested_clusters", "anisotropic", "multimodal_class",
    "varying_density", "imbalanced_density",
)


def _allocate(n: int, ratio: float) -> Tuple[int, int]:
    minority = max(2, int(round(n / (1.0 + max(ratio, 1e-6)))))
    return n - minority, minority


def _spirals(n: int, rng: np.random.Generator, turns: float, width: float) -> Tuple[np.ndarray, np.ndarray]:
    n0, n1 = _allocate(n, 1.0)
    parts, labels = [], []
    for label, count, phase in ((0, n0, 0.0), (1, n1, np.pi)):
        t = np.linspace(0.15, turns * 2 * np.pi, count)
        radius = t / (turns * 2 * np.pi)
        angle = t + phase
        points = np.column_stack([radius * np.cos(angle), radius * np.sin(angle)])
        points += rng.normal(scale=width, size=points.shape)
        parts.append(points); labels.append(np.full(count, label, dtype=int))
    return np.vstack(parts), np.concatenate(labels)


def _base(family: str, n: int, rng: np.random.Generator, seed: int, p: Dict[str, Any]):
    separation = float(p.get("separation", 2.0))
    overlap = float(p.get("overlap", 0.15))
    width = float(p.get("manifold_width", 0.08))
    density_ratio = float(p.get("density_ratio", 4.0))
    imbalance = float(p.get("imbalance_ratio", 1.0))
    if family == "gaussian_blobs":
        return make_blobs(n_samples=n, centers=[(-separation / 2, 0), (separation / 2, 0)],
                          cluster_std=max(overlap, 0.01), random_state=seed)
    if family == "moons":
        return make_moons(n_samples=n, noise=max(width, 0.0), random_state=seed)
    if family == "circles":
        return make_circles(n_samples=n, noise=max(width, 0.0), factor=float(p.get("radius_ratio", 0.45)), random_state=seed)
    if family == "xor":
        X = rng.uniform(-1, 1, size=(n, 2)); y = ((X[:, 0] >= 0) ^ (X[:, 1] >= 0)).astype(int)
        X += rng.normal(scale=overlap, size=X.shape); return X, y
    if family == "checkerboard":
        cells = int(p.get("cells", 4)); X = rng.uniform(0, cells, size=(n, 2))
        y = ((np.floor(X[:, 0]) + np.floor(X[:, 1])) % 2).astype(int)
        X += rng.normal(scale=width, size=X.shape); return X, y
    if family == "spirals":
        return _spirals(n, rng, float(p.get("curvature", 2.0)), width)
    if family == "thin_manifold":
        x = rng.uniform(-2, 2, n); y = (x >= 0).astype(int)
        X = np.column_stack([x, np.sin(float(p.get("curvature", 3.0)) * x)])
        X += rng.normal(scale=width, size=X.shape); return X, y
    if family == "nested_clusters":
        y = rng.integers(0, 2, n); angle = rng.uniform(0, 2 * np.pi, n)
        radius = np.where(y == 0, 0.35, 1.0) + rng.normal(scale=width, size=n)
        return np.column_stack([radius * np.cos(angle), radius * np.sin(angle)]), y
    if family == "anisotropic":
        X, y = make_blobs(n_samples=n, centers=2, cluster_std=1.0, random_state=seed)
        transform = np.array([[separation, 0.85 * separation], [0.0, max(width, 0.05)]])
        return X @ transform, y
    if family == "multimodal_class":
        centers = [(-separation, -separation), (separation, separation), (-separation, separation), (separation, -separation)]
        X, component = make_blobs(n_samples=n, centers=centers, cluster_std=max(overlap, 0.03), random_state=seed)
        return X, (component >= 2).astype(int)
    if family == "varying_density":
        n0, n1 = _allocate(n, 1.0)
        X0 = rng.normal(loc=(-separation / 2, 0), scale=max(width, 0.02), size=(n0, 2))
        X1 = rng.normal(loc=(separation / 2, 0), scale=max(width * density_ratio, 0.02), size=(n1, 2))
        return np.vstack([X0, X1]), np.r_[np.zeros(n0, int), np.ones(n1, int)]
    if family == "imbalanced_density":
        n0, n1 = _allocate(n, imbalance)
        X0 = rng.normal(loc=(-separation / 2, 0), scale=max(width, 0.02), size=(n0, 2))
        X1 = rng.normal(loc=(separation / 2, 0), scale=max(width / density_ratio, 0.02), size=(n1, 2))
        return np.vstack([X0, X1]), np.r_[np.zeros(n0, int), np.ones(n1, int)]
    raise ValueError(f"unknown family {family!r}; choose from {FAMILIES}")


def _apply_label_noise(X, y, rng, kind: str, rate: float):
    y = y.copy(); count = min(len(y), int(round(rate * len(y))))
    if count <= 0 or kind == "none": return y, []
    if kind == "symmetric": candidates = np.arange(len(y))
    elif kind == "boundary":
        c0, c1 = X[y == 0].mean(0), X[y == 1].mean(0)
        margin = np.abs(np.linalg.norm(X - c0, axis=1) - np.linalg.norm(X - c1, axis=1))
        candidates = np.argsort(margin)[:max(count, 1)]
    elif kind == "cluster_specific": candidates = np.flatnonzero((y == 0) & (X[:, 0] > np.median(X[:, 0])))
    elif kind == "asymmetric": candidates = np.flatnonzero(y == 0)
    else: raise ValueError(f"unknown label_noise kind: {kind}")
    count = min(count, len(candidates)); chosen = rng.choice(candidates, count, replace=False)
    y[chosen] = 1 - y[chosen]; return y, chosen.tolist()


def generate(family: str, n_samples: int = 500, seed: int = 42, ambient_dimension: int = 2, **parameters):
    """Return `(X, y, metadata)` with every stochastic choice controlled by seed."""
    if family not in FAMILIES: raise ValueError(f"unknown family: {family}")
    if n_samples < 8 or ambient_dimension < 2: raise ValueError("n_samples >= 8 and ambient_dimension >= 2 required")
    rng = np.random.default_rng(seed)
    X, y = _base(family, n_samples, rng, seed, parameters)
    permutation = rng.permutation(len(y)); X, y = np.asarray(X)[permutation], np.asarray(y, int)[permutation]
    intrinsic = X.shape[1]
    if ambient_dimension > intrinsic:
        projection = rng.normal(size=(intrinsic, ambient_dimension)) / np.sqrt(intrinsic)
        X = X @ projection
    feature_noise = float(parameters.get("feature_noise", 0.0))
    if feature_noise: X = X + rng.normal(scale=feature_noise, size=X.shape)
    outlier_rate = float(parameters.get("outlier_rate", 0.0)); outlier_count = int(round(len(y) * outlier_rate))
    outlier_indices = []
    if outlier_count:
        outlier_indices = rng.choice(len(y), min(outlier_count, len(y)), replace=False).tolist()
        span = np.maximum(np.ptp(X, axis=0), 1.0)
        X[outlier_indices] = rng.uniform(X.min(0) - span, X.max(0) + span, size=(len(outlier_indices), X.shape[1]))
    y, flipped = _apply_label_noise(X, y, rng, str(parameters.get("label_noise", "none")), float(parameters.get("noise_rate", 0.0)))
    metadata = {"family": family, "seed": seed, "n_samples": len(y), "intrinsic_dimension": intrinsic,
                "ambient_dimension": ambient_dimension, "parameters": parameters,
                "label_flips": flipped, "outlier_indices": outlier_indices}
    return X.astype(float), y.astype(int), metadata

