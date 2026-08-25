from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.tree import DecisionTreeClassifier

from baselines.gbc import GranularBallClassifier


@dataclass(frozen=True)
class ReleasedSummary:
    method: str
    variant: str
    centers: np.ndarray
    radii: np.ndarray
    counts: np.ndarray
    purities: np.ndarray
    labels: np.ndarray
    members: tuple[np.ndarray, ...]
    disclose_radius: bool
    disclose_count: bool
    disclose_purity: bool


def all_releases(X: np.ndarray, y: np.ndarray, *, seed: int, purity: float) -> list[ReleasedSummary]:
    gbc = GranularBallClassifier(purity=purity, min_samples=2, random_state=seed).fit(X, y)
    gb_members = tuple(ball.members for ball in gbc.balls_)
    k = len(gb_members)
    partitions = {
        "raw": tuple(np.array([i]) for i in range(len(X))),
        "kmeans": _groups(KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(X)),
        "hierarchical": _groups(AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)),
        "random": _random_groups(len(X), k, seed),
        "tree": _tree_groups(X, y, k, seed),
        "granular_ball": gb_members,
    }
    releases = []
    for method, members in partitions.items():
        base = _summarize(method, X, y, members)
        if method == "raw":
            releases.append(_variant(base, "R0_raw_samples", False, False, False))
        elif method == "kmeans":
            releases.extend(
                [
                    _variant(base, "R1_center", False, False, False),
                    _variant(base, "R2_center_count", False, True, False),
                    _variant(base, "R3_center_radius", True, False, False),
                    _variant(base, "R4_center_radius_count", True, True, False),
                ]
            )
        elif method == "granular_ball":
            releases.extend(
                [
                    _variant(base, "R5_center", False, False, False),
                    _variant(base, "R6_center_radius", True, False, False),
                    _variant(base, "R7_center_radius_count", True, True, False),
                    _variant(base, "R8_center_radius_count_purity", True, True, True),
                ]
            )
        else:
            releases.append(_variant(base, "matched_full", True, True, True))
    return releases


def _summarize(method: str, X: np.ndarray, y: np.ndarray, members: tuple[np.ndarray, ...]) -> ReleasedSummary:
    centers, radii, counts, purities, labels = [], [], [], [], []
    for indices in members:
        center = X[indices].mean(axis=0)
        values, class_counts = np.unique(y[indices], return_counts=True)
        centers.append(center)
        radii.append(np.linalg.norm(X[indices] - center, axis=1).mean())
        counts.append(len(indices))
        purities.append(class_counts.max() / len(indices))
        labels.append(values[np.argmax(class_counts)])
    return ReleasedSummary(
        method=method,
        variant="",
        centers=np.asarray(centers),
        radii=np.maximum(np.asarray(radii), 1e-12),
        counts=np.asarray(counts),
        purities=np.asarray(purities),
        labels=np.asarray(labels),
        members=members,
        disclose_radius=False,
        disclose_count=False,
        disclose_purity=False,
    )


def _variant(base: ReleasedSummary, name: str, radius: bool, count: bool, purity: bool) -> ReleasedSummary:
    return ReleasedSummary(
        method=base.method,
        variant=name,
        centers=base.centers,
        radii=base.radii,
        counts=base.counts,
        purities=base.purities,
        labels=base.labels,
        members=base.members,
        disclose_radius=radius,
        disclose_count=count,
        disclose_purity=purity,
    )


def release_from_groups(
    method: str,
    variant: str,
    X: np.ndarray,
    y: np.ndarray,
    members: tuple[np.ndarray, ...],
    *,
    radius: bool = True,
    count: bool = True,
    purity: bool = True,
) -> ReleasedSummary:
    """Build a release for an externally defined matched-size partition."""
    return _variant(_summarize(method, X, y, members), variant, radius, count, purity)


def _groups(labels: np.ndarray) -> tuple[np.ndarray, ...]:
    return tuple(np.flatnonzero(labels == value) for value in np.unique(labels))


def _random_groups(n: int, k: int, seed: int) -> tuple[np.ndarray, ...]:
    return tuple(np.sort(group) for group in np.array_split(np.random.default_rng(seed).permutation(n), k))


def _tree_groups(X: np.ndarray, y: np.ndarray, k: int, seed: int) -> tuple[np.ndarray, ...]:
    if k == 1:
        return (np.arange(len(X)),)
    model = DecisionTreeClassifier(
        max_leaf_nodes=k,
        min_samples_leaf=max(2, len(X) // max(4 * k, 1)),
        random_state=seed,
    ).fit(X, y)
    return _groups(model.apply(X))
