"""Map samples to label-free-at-query-time granular structural features."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import pairwise_distances

from .generator import StableGranularBallGenerator


STRUCTURAL_FEATURE_NAMES = (
    "gb_distance_to_center",
    "gb_normalized_distance_to_center",
    "gb_radius",
    "gb_log_size",
    "gb_purity",
    "gb_label_entropy",
    "gb_local_density",
    "gb_depth",
    "gb_nearest_same_label_ball_distance",
    "gb_nearest_other_label_ball_distance",
    "gb_margin",
    "gb_neighbor_ball_count",
)


def structural_features(
    generator: StableGranularBallGenerator,
    X: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return structural features and assigned ball IDs without query labels."""
    X = np.asarray(X, dtype=float)
    distances = pairwise_distances(X, generator.centers_)
    boundary = distances - generator.radii_[None, :]
    assigned = np.argmin(boundary, axis=1)
    rows = np.empty((len(X), len(STRUCTURAL_FEATURE_NAMES)), dtype=float)
    for row_index, ball_index in enumerate(assigned):
        center_distance = distances[row_index, ball_index]
        radius = generator.radii_[ball_index]
        label = generator.labels_encoded_[ball_index]
        same = np.flatnonzero(generator.labels_encoded_ == label)
        same = same[same != ball_index]
        other = np.flatnonzero(generator.labels_encoded_ != label)
        nearest_same = float(distances[row_index, same].min()) if len(same) else center_distance
        nearest_other = float(distances[row_index, other].min()) if len(other) else center_distance
        neighbor_count = int(
            np.sum(
                distances[row_index]
                <= radius + generator.radii_
            )
        ) - 1
        local_density = np.log1p(generator.sizes_[ball_index]) / (radius + 1e-12)
        rows[row_index] = [
            center_distance,
            center_distance / (radius + 1e-12),
            radius,
            np.log1p(generator.sizes_[ball_index]),
            generator.purities_[ball_index],
            generator.entropies_[ball_index],
            local_density,
            generator.depths_[ball_index],
            nearest_same,
            nearest_other,
            nearest_other - center_distance,
            max(neighbor_count, 0),
        ]
    if not np.isfinite(rows).all():
        raise RuntimeError("GB structural features contain non-finite values")
    return rows, assigned

