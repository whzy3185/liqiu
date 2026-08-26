"""Index-backed, source-faithful GBABS.

This module mirrors the pinned official RD_GBG.py and GBABS.py control flow.
It changes only ball storage from complete data rows to immutable global arrays
plus member indices. In particular, it retains NumPy's default argsort calls,
the original global NumPy RNG sequence, and original discovery order.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class IndexBall:
    member_indices: np.ndarray
    center: np.ndarray
    radius: float
    label: float


@dataclass(frozen=True)
class ExactGBABSResult:
    balls: tuple[IndexBall, ...]
    boundary_sample_indices: tuple[int, ...]
    low_density_records: tuple[tuple[int, int], ...]
    outlier_records: tuple[tuple[int, int], ...]


class ExactGBABS:
    def __init__(self, x: np.ndarray, y: np.ndarray, sample_ids: np.ndarray, rho: int) -> None:
        self.x = np.asarray(x, dtype=np.float64)
        self.y = np.asarray(y, dtype=np.float64)
        self.sample_ids = np.asarray(sample_ids, dtype=np.int64)
        if len(self.x) != len(self.y) or len(self.x) != len(self.sample_ids):
            raise ValueError("X, y, and sample_ids must have equal row counts")
        if len(np.unique(self.sample_ids)) != len(self.sample_ids):
            raise ValueError("sample_ids must be unique")
        self.rho = rho
        self._sample_to_position = {int(sid): pos for pos, sid in enumerate(self.sample_ids)}
        self._low_density: list[tuple[int, int]] = []
        self._outliers: list[tuple[int, int]] = []

    def _random_centers(self, remaining: np.ndarray) -> list[int]:
        excluded = {sample_id for sample_id, _ in self._low_density}
        filtered = remaining[np.array([int(idx) not in excluded for idx in remaining], dtype=bool)]
        if len(filtered) == 0:
            return []
        label_counts = Counter(self.y[filtered])
        sorted_labels = sorted(label_counts, key=label_counts.get, reverse=True)
        centers: list[int] = []
        for label in sorted_labels:
            class_members = filtered[self.y[filtered] == label]
            if len(class_members):
                centers.append(int(class_members[np.random.choice(len(class_members), size=1, replace=False)[0]]))
        return centers

    def _distance(self, point: np.ndarray, members: np.ndarray) -> np.ndarray:
        return np.sqrt(np.sum((point - self.x[members]) ** 2, axis=1))

    def _surface_distances(self, center_idx: int, balls: list[IndexBall]) -> list[float]:
        point = self.x[center_idx]
        return [float(np.sqrt(np.sum((point - ball.center) ** 2)) - ball.radius) for ball in balls]

    def _detect_outlier(self, sorted_indices: np.ndarray, k: int, center_label: float) -> int:
        homogeneous_count = int(np.sum(self.y[sorted_indices[:k]] == center_label) - 1)
        if homogeneous_count == 0:
            result = 0
        elif homogeneous_count == k - 1:
            result = 1
        else:
            result = 2
        self._outliers.append((int(self.sample_ids[sorted_indices[0]]), result))
        return result

    def _generate_balls(self, balls: list[IndexBall], remaining_input: np.ndarray) -> tuple[list[IndexBall], np.ndarray, int]:
        new_balls: list[IndexBall] = []
        temporary_balls = balls.copy()
        remaining = remaining_input.copy()
        centers = self._random_centers(remaining_input)
        if not centers:
            return new_balls, remaining, 1
        for center_idx in centers:
            center_label = self.y[center_idx]
            distances = self._distance(self.x[center_idx], remaining)
            order = distances.argsort()
            sorted_indices = remaining[order]
            sorted_distances = distances[order]
            heterogeneous = np.argwhere(self.y[sorted_indices] != center_label)
            if len(heterogeneous):
                heter_index = int(heterogeneous[0][0])
                if heter_index == 1:
                    outcome = self._detect_outlier(sorted_indices, self.rho, center_label)
                    if outcome == 0:
                        remaining = remaining[remaining != center_idx]
                        continue
                    if outcome == 2:
                        self._low_density.append((int(self.sample_ids[center_idx]), 0))
                        continue
                    sorted_indices = np.delete(sorted_indices, 1)
                    sorted_distances = np.delete(sorted_distances, 1)
                    heterogeneous = np.argwhere(self.y[sorted_indices] != center_label)
                    if len(heterogeneous):
                        heter_index = int(heterogeneous[0][0])
                        temporary_radius = float(sorted_distances[heter_index - 1])
                    else:
                        temporary_radius = float(sorted_distances[-1])
                else:
                    temporary_radius = float(sorted_distances[heter_index - 1])
            else:
                heter_index = len(sorted_indices)
                temporary_radius = float(sorted_distances[-1])
            minimum_ball_distance = min(self._surface_distances(center_idx, temporary_balls), default=np.inf)
            if temporary_radius <= minimum_ball_distance:
                radius = temporary_radius
                member_indices = sorted_indices[:heter_index]
                remaining = sorted_indices[heter_index:]
            else:
                within = np.argwhere(sorted_distances <= minimum_ball_distance)
                if len(within) <= 1:
                    self._low_density.append((int(self.sample_ids[center_idx]), 1))
                    continue
                max_index = int(np.max(within))
                radius = float(sorted_distances[max_index])
                member_indices = sorted_indices[: max_index + 1]
                remaining = sorted_indices[max_index + 1 :]
            ball = IndexBall(member_indices.copy(), self.x[center_idx].copy(), radius, float(center_label))
            new_balls.append(ball)
            temporary_balls.append(ball)
        return new_balls, remaining, 0

    def _generate_ball_list(self) -> list[IndexBall]:
        balls: list[IndexBall] = []
        remaining = np.arange(len(self.x), dtype=np.int64)
        while True:
            new_balls, remaining, ended = self._generate_balls(balls, remaining)
            if ended:
                break
            balls.extend(ball for ball in new_balls if len(ball.member_indices))
            if len(remaining) == len(np.unique(self.y[remaining])):
                break
        for sample_id, status in self._low_density:
            if status != 1:
                continue
            position = self._sample_to_position[sample_id]
            if position in remaining:
                balls.append(IndexBall(np.array([position], dtype=np.int64), self.x[position].copy(), 0.0, float(self.y[position])))
                remaining = remaining[remaining != position]
        return balls

    def _sample_boundaries(self, balls: list[IndexBall]) -> tuple[int, ...]:
        centers = np.array([ball.center for ball in balls])
        selected: list[int] = []
        selected_set: set[int] = set()
        for feature_dim in range(self.x.shape[1]):
            ordered_balls = centers[:, feature_dim].argsort()
            for offset in range(len(ordered_balls) - 1):
                current = balls[int(ordered_balls[offset])]
                following = balls[int(ordered_balls[offset + 1])]
                if current.label == following.label:
                    continue
                current_values = self.x[current.member_indices, feature_dim]
                following_values = self.x[following.member_indices, feature_dim]
                current_members = current.member_indices[current_values == np.max(current_values)]
                following_members = following.member_indices[following_values == np.min(following_values)]
                for position in np.concatenate((current_members, following_members)):
                    sample_id = int(self.sample_ids[position])
                    if sample_id not in selected_set:
                        selected_set.add(sample_id)
                        selected.append(sample_id)
        return tuple(selected)

    def sample(self, seed: int | None = None) -> ExactGBABSResult:
        if seed is not None:
            np.random.seed(seed)
        balls = self._generate_ball_list()
        boundary = self._sample_boundaries(balls)
        return ExactGBABSResult(tuple(balls), boundary, tuple(self._low_density), tuple(self._outliers))
