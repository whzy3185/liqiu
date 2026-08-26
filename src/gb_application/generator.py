"""Top-down purity-split granular balls with auditable membership and depth."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans


@dataclass(frozen=True)
class BallSummary:
    members: np.ndarray
    center: np.ndarray
    radius: float
    label: int
    purity: float
    class_counts: np.ndarray
    entropy: float
    depth: int


class StableGranularBallGenerator:
    """The repository's stable purity-split GBC logic with depth bookkeeping.

    A ball is split into as many KMeans children as labels present in the ball.
    Splitting stops at the requested purity, minimum size, one-class content, or
    a global low-compute ball cap. This is a feature generator, not a new GB
    algorithm.
    """

    def __init__(
        self,
        purity: float = 0.9,
        min_samples: int = 5,
        random_state: int = 5,
        max_balls: int = 256,
    ) -> None:
        if not 0.5 <= purity <= 1:
            raise ValueError("purity must lie in [0.5, 1]")
        if min_samples < 2 or max_balls < 2:
            raise ValueError("min_samples and max_balls must be at least 2")
        self.purity = purity
        self.min_samples = min_samples
        self.random_state = random_state
        self.max_balls = max_balls

    def fit(self, X: np.ndarray, y: np.ndarray) -> "StableGranularBallGenerator":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y).reshape(-1)
        if X.ndim != 2 or len(X) != len(y) or len(y) < 2:
            raise ValueError("X/y shapes are invalid")
        if not np.isfinite(X).all():
            raise ValueError("X must be finite before GB generation")
        self.classes_, encoded = np.unique(y, return_inverse=True)
        self.X_ = X
        self.y_encoded_ = encoded
        pending: list[tuple[np.ndarray, int]] = [(np.arange(len(y)), 0)]
        final: list[BallSummary] = []
        while pending:
            members, depth = pending.pop(0)
            ball = self._summarize(members, depth)
            labels = np.unique(encoded[members])
            can_split = (
                ball.purity < self.purity
                and len(members) > self.min_samples
                and len(labels) >= 2
                and len(final) + len(pending) + len(labels) <= self.max_balls
            )
            if not can_split:
                final.append(ball)
                continue
            assignment = KMeans(
                n_clusters=len(labels),
                n_init=10,
                random_state=self.random_state + depth,
            ).fit_predict(X[members])
            children = [members[assignment == cluster] for cluster in range(len(labels))]
            children = [child for child in children if len(child)]
            if len(children) < 2:
                final.append(ball)
            else:
                pending = [(child, depth + 1) for child in children] + pending
        self.balls_ = final
        self.centers_ = np.vstack([ball.center for ball in final])
        self.radii_ = np.asarray([ball.radius for ball in final])
        self.labels_encoded_ = np.asarray([ball.label for ball in final])
        self.sizes_ = np.asarray([len(ball.members) for ball in final])
        self.purities_ = np.asarray([ball.purity for ball in final])
        self.entropies_ = np.asarray([ball.entropy for ball in final])
        self.depths_ = np.asarray([ball.depth for ball in final])
        return self

    def _summarize(self, members: np.ndarray, depth: int) -> BallSummary:
        points = self.X_[members]
        center = points.mean(axis=0)
        radius = float(np.linalg.norm(points - center, axis=1).mean())
        counts = np.bincount(self.y_encoded_[members], minlength=len(self.classes_))
        label = int(np.argmax(counts))
        probabilities = counts[counts > 0] / len(members)
        entropy = float(-np.sum(probabilities * np.log(probabilities)))
        if len(self.classes_) > 1:
            entropy /= float(np.log(len(self.classes_)))
        return BallSummary(
            members=np.asarray(members),
            center=center,
            radius=max(radius, 1e-12),
            label=label,
            purity=float(counts[label] / len(members)),
            class_counts=counts,
            entropy=entropy,
            depth=depth,
        )

