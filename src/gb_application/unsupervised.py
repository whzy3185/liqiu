"""Unsupervised recursive ball covers and matched-KMeans structural controls."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances


UNSUPERVISED_FEATURE_NAMES = (
    "local_distance_to_center",
    "local_normalized_distance",
    "local_radius",
    "local_log_size",
    "local_density",
    "local_depth",
    "local_nearest_center_distance",
    "local_center_separation",
    "local_boundary_margin",
    "local_neighbor_region_count",
)


@dataclass(frozen=True)
class Region:
    members: np.ndarray
    center: np.ndarray
    radius: float
    depth: int


class RecursiveBallCover:
    """Label-free two-means cover, splitting the most dispersed eligible region."""

    def __init__(self, max_regions: int = 128, min_samples: int = 20, random_state: int = 0) -> None:
        if max_regions < 2 or min_samples < 2:
            raise ValueError("max_regions and min_samples must be at least two")
        self.max_regions = max_regions
        self.min_samples = min_samples
        self.random_state = random_state

    def fit(self, X: np.ndarray) -> "RecursiveBallCover":
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or len(X) < 2 or not np.isfinite(X).all():
            raise ValueError("X must be finite two-dimensional data")
        self.X_ = X
        pending = [self._region(np.arange(len(X)), 0)]
        while len(pending) < self.max_regions:
            eligible = [
                (index, region)
                for index, region in enumerate(pending)
                if len(region.members) >= 2 * self.min_samples and region.radius > 0
            ]
            if not eligible:
                break
            index, parent = max(eligible, key=lambda pair: pair[1].radius * np.sqrt(len(pair[1].members)))
            labels = KMeans(n_clusters=2, n_init=10, random_state=self.random_state + parent.depth).fit_predict(X[parent.members])
            left = parent.members[labels == 0]
            right = parent.members[labels == 1]
            if min(len(left), len(right)) < self.min_samples:
                # Mark it non-splittable by moving it to a list whose size makes
                # it ineligible on future passes.
                pending[index] = Region(parent.members, parent.center, 0.0, parent.depth)
                continue
            pending[index : index + 1] = [self._region(left, parent.depth + 1), self._region(right, parent.depth + 1)]
        self.regions_ = pending
        self.centers_ = np.vstack([region.center for region in pending])
        self.radii_ = np.asarray([max(region.radius, 1e-12) for region in pending])
        self.sizes_ = np.asarray([len(region.members) for region in pending])
        self.depths_ = np.asarray([region.depth for region in pending])
        return self

    def _region(self, members: np.ndarray, depth: int) -> Region:
        points = self.X_[members]
        center = points.mean(axis=0)
        return Region(members, center, float(np.linalg.norm(points - center, axis=1).mean()), depth)


class MatchedKMeansRegions:
    """KMeans regions with the same region count as an unsupervised ball cover."""

    def __init__(self, n_regions: int, random_state: int = 0) -> None:
        self.n_regions = n_regions
        self.random_state = random_state

    def fit(self, X: np.ndarray) -> "MatchedKMeansRegions":
        X = np.asarray(X, dtype=float)
        labels = KMeans(n_clusters=self.n_regions, n_init=20, random_state=self.random_state).fit_predict(X)
        centers, radii, sizes = [], [], []
        for region in range(self.n_regions):
            points = X[labels == region]
            center = points.mean(axis=0)
            centers.append(center)
            radii.append(max(float(np.linalg.norm(points - center, axis=1).mean()), 1e-12))
            sizes.append(len(points))
        self.centers_ = np.asarray(centers)
        self.radii_ = np.asarray(radii)
        self.sizes_ = np.asarray(sizes)
        self.depths_ = np.zeros(self.n_regions, dtype=int)
        return self


def unsupervised_features(regions: RecursiveBallCover | MatchedKMeansRegions, X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    distances = pairwise_distances(X, regions.centers_)
    boundary = distances - regions.radii_[None, :]
    selected = np.argmin(boundary, axis=1)
    rows = np.empty((len(X), len(UNSUPERVISED_FEATURE_NAMES)), dtype=float)
    for row, region in enumerate(selected):
        center_distance = distances[row, region]
        all_other = np.delete(distances[row], region)
        nearest = float(all_other.min()) if len(all_other) else center_distance
        own_boundary = boundary[row, region]
        other_boundary = np.delete(boundary[row], region)
        margin = float(other_boundary.min() - own_boundary) if len(other_boundary) else 0.0
        overlap = int(np.sum(distances[row] <= regions.radii_[region] + regions.radii_)) - 1
        radius = regions.radii_[region]
        rows[row] = [
            center_distance,
            center_distance / radius,
            radius,
            np.log1p(regions.sizes_[region]),
            np.log1p(regions.sizes_[region]) / radius,
            regions.depths_[region],
            nearest,
            nearest - center_distance,
            margin,
            max(overlap, 0),
        ]
    if not np.isfinite(rows).all():
        raise RuntimeError("unsupervised local features contain non-finite values")
    return rows


def uniform_fit_subset(n_samples: int, cap: int | None, seed: int) -> np.ndarray:
    if cap is None or n_samples <= cap:
        return np.arange(n_samples)
    return np.sort(np.random.default_rng(seed).choice(n_samples, size=cap, replace=False))
