"""Instrumented parameter-free adaptive granular-ball generator.

Clean-room Python implementation of the public adaptive-GBC procedure described
by Xia et al. (2024): heterogeneous-label seeded refinement, weighted-purity
acceptance, overlap-driven re-splitting, and global reassignment from learned
centers. It is a research control, not author-verified code.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans

from baselines.gbc.model import Ball


@dataclass
class _Proposal:
    members: np.ndarray
    center: np.ndarray
    depth: int


class AdaptiveGranularBallClassifier:
    """Parameter-free adaptive GBC with native boundary-distance routing."""

    def __init__(self, random_state: int = 1, max_depth: int = 12, max_overlap_rounds: int = 6):
        self.random_state = random_state
        self.max_depth = max_depth
        self.max_overlap_rounds = max_overlap_rounds

    def _stats(self, members: np.ndarray, center: np.ndarray):
        labels, counts = np.unique(self.y_[members], return_counts=True)
        best = int(np.argmax(counts))
        label = labels[best]
        purity = float(counts[best] / counts.sum())
        radius = float(np.linalg.norm(self.X_[members] - center, axis=1).mean())
        full_counts = np.array([np.sum(self.y_[members] == cls) for cls in self.classes_])
        return label, purity, radius, full_counts

    def _split(self, members: np.ndarray, center: np.ndarray, rng: np.random.Generator):
        labels = np.unique(self.y_[members])
        nearest = members[int(np.argmin(np.linalg.norm(self.X_[members] - center, axis=1)))]
        seed_label = self.y_[nearest]
        centers = [center]
        for label in labels:
            if label == seed_label:
                continue
            candidates = members[self.y_[members] == label]
            centers.append(self.X_[int(rng.choice(candidates))])
        if len(centers) == 1 and len(members) > 1:
            farthest = members[int(np.argmax(np.linalg.norm(self.X_[members] - center, axis=1)))]
            centers.append(self.X_[farthest])
        centers = np.asarray(centers)
        distances = np.linalg.norm(self.X_[members, None, :] - centers[None, :, :], axis=2)
        assignment = np.argmin(distances, axis=1)
        return [
            _Proposal(members[assignment == index], candidate.copy(), 0)
            for index, candidate in enumerate(centers)
            if np.any(assignment == index)
        ]

    def fit(self, X, y):
        self.X_ = np.asarray(X, dtype=float)
        self.y_ = np.asarray(y)
        self.classes_ = np.unique(self.y_)
        rng = np.random.default_rng(self.random_state)
        self.safety_cap_hit_ = False

        # The public reference removes duplicate rows before adaptive generation.
        _, unique_index = np.unique(self.X_, axis=0, return_index=True)
        unique_index = np.sort(unique_index)
        self.X_ = self.X_[unique_index]
        self.y_ = self.y_[unique_index]
        original_index = unique_index
        root = np.arange(len(self.y_))
        initial_center = self.X_[int(rng.integers(len(root)))]
        initial_children = self._split(root, initial_center, rng)
        purity_floor = max(self._stats(child.members, child.center)[1] for child in initial_children)

        pending = [_Proposal(root, initial_center, 0)]
        proposals: list[_Proposal] = []
        while pending:
            proposal = pending.pop(0)
            _, parent_purity, _, _ = self._stats(proposal.members, proposal.center)
            if len(proposal.members) <= 1 or proposal.depth >= self.max_depth:
                if proposal.depth >= self.max_depth and parent_purity < 1:
                    self.safety_cap_hit_ = True
                proposals.append(proposal)
                continue
            children = self._split(proposal.members, proposal.center, rng)
            if len(children) < 2 or max(len(child.members) for child in children) == len(proposal.members):
                proposals.append(proposal)
                continue
            weighted_child_purity = sum(
                self._stats(child.members, child.center)[1] * len(child.members) / len(proposal.members)
                for child in children
            )
            if parent_purity <= purity_floor or weighted_child_purity > parent_purity:
                pending.extend(_Proposal(child.members, child.center, proposal.depth + 1) for child in children)
            else:
                proposals.append(proposal)

        # De-overlap only differently labeled proposals, as in the reference.
        for _ in range(self.max_overlap_rounds):
            stats = [self._stats(node.members, node.center) for node in proposals]
            overlap = set()
            for i in range(len(proposals)):
                for j in range(i + 1, len(proposals)):
                    if stats[i][0] == stats[j][0]:
                        continue
                    if np.linalg.norm(proposals[i].center - proposals[j].center) < stats[i][2] + stats[j][2]:
                        overlap.update((i, j))
            if not overlap:
                break
            updated: list[_Proposal] = []
            for index, node in enumerate(proposals):
                if index not in overlap or len(node.members) <= 1 or node.depth >= self.max_depth:
                    if index in overlap and node.depth >= self.max_depth:
                        self.safety_cap_hit_ = True
                    updated.append(node)
                    continue
                children = self._split(node.members, node.center, rng)
                if len(children) < 2:
                    updated.append(node)
                else:
                    updated.extend(_Proposal(child.members, child.center, node.depth + 1) for child in children)
            proposals = updated
        else:
            self.safety_cap_hit_ = True

        initial_centers = np.vstack([node.center for node in proposals])
        model = KMeans(n_clusters=len(initial_centers), init=initial_centers, n_init=1, random_state=self.random_state)
        assignment = model.fit_predict(self.X_)
        self.balls_ = []
        self.depths_ = []
        for cluster_id, center in enumerate(model.cluster_centers_):
            members = np.flatnonzero(assignment == cluster_id)
            if len(members) == 0:
                continue
            label, purity, radius, counts = self._stats(members, center)
            self.balls_.append(Ball(original_index[members], center, radius, label, purity, counts))
            self.depths_.append(proposals[cluster_id].depth)
        return self

    def _boundary_distances(self, X):
        X = np.asarray(X, dtype=float)
        centers = np.vstack([ball.center for ball in self.balls_])
        radii = np.asarray([ball.radius for ball in self.balls_])
        return np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2) - radii

    def route_native(self, X):
        return np.argmin(self._boundary_distances(X), axis=1)

    def predict(self, X):
        route = self.route_native(X)
        return np.asarray([self.balls_[index].label for index in route])
