"""Synthetic-oracle adaptive purity validity audit (frozen v1 definitions)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from baselines.gbc import GranularBallClassifier


THRESHOLDS = (.70, .80, .90, .95, .99, 1.0)


@dataclass
class GeometryNode:
    indices: np.ndarray
    center: np.ndarray
    depth: int
    children: list["GeometryNode"] = field(default_factory=list)


class XOnlyMaximalGranulationTree:
    """Audited geometry-only hierarchy; labels are attached only after fitting."""
    def __init__(self, min_leaf_support: int = 2, max_depth: int = 30, random_state: int = 1):
        self.min_leaf_support, self.max_depth, self.random_state = min_leaf_support, max_depth, random_state
    def fit(self, x: np.ndarray):
        self.x_ = np.asarray(x, float)
        self.root = _geometry_tree(self.x_, np.arange(len(self.x_)), self.random_state, max_depth=self.max_depth, min_leaf_support=self.min_leaf_support)
        return self


def _geometry_tree(x: np.ndarray, indices: np.ndarray, seed: int, depth: int = 0, max_depth: int = 30, min_leaf_support: int = 2) -> GeometryNode:
    values = x[indices]
    node = GeometryNode(indices, values.mean(axis=0), depth)
    if len(indices) <= min_leaf_support or depth >= max_depth:
        return node
    assignment = KMeans(2, random_state=seed + depth, n_init="auto").fit_predict(values)
    if len(np.unique(assignment)) < 2:
        return node
    node.children = [_geometry_tree(x, indices[assignment == part], seed, depth + 1, max_depth, min_leaf_support) for part in (0, 1)]
    return node


def _purity(node: GeometryNode, y: np.ndarray) -> tuple[float, int]:
    values, counts = np.unique(y[node.indices], return_counts=True)
    best = int(np.argmax(counts))
    return float(counts[best] / counts.sum()), int(values[best])


def _cut_geometry(node: GeometryNode, y: np.ndarray, tau: float) -> list[GeometryNode]:
    value, _ = _purity(node, y)
    if not node.children or value >= tau:
        return [node]
    return _cut_geometry(node.children[0], y, tau) + _cut_geometry(node.children[1], y, tau)


def sample_family(name: str, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    modes = rng.integers(0, 4, n)
    centers = np.array([[-2, -2], [-2, 2], [2, -2], [2, 2]], float)
    x = centers[modes] + rng.normal(0, .9, (n, 2))
    if name == "null_label":
        probability = np.full(n, .5)
    elif name == "smooth_weak":
        probability = 1 / (1 + np.exp(-.55 * x[:, 0]))
    elif name == "smooth_moderate":
        probability = 1 / (1 + np.exp(-1.5 * x[:, 0]))
    elif name == "piecewise":
        probability = np.array([.60, .70, .80, .95])[modes]
    else:
        raise ValueError(name)
    return x, (rng.random(n) < probability).astype(int)


def _route_tree(root: GeometryNode, leaves: list[GeometryNode], x: np.ndarray) -> np.ndarray:
    ids = {id(node): index for index, node in enumerate(leaves)}
    output = np.empty(len(x), dtype=int)
    def visit(node: GeometryNode, positions: np.ndarray) -> None:
        if id(node) in ids:
            output[positions] = ids[id(node)]
            return
        distances = np.column_stack([np.linalg.norm(x[positions] - child.center, axis=1) for child in node.children])
        choice = np.argmin(distances, axis=1)
        for child_id, child in enumerate(node.children):
            visit(child, positions[choice == child_id])
    visit(root, np.arange(len(x)))
    return output


def _route_gbc(model, x: np.ndarray) -> tuple[np.ndarray, list]:
    # Keep the frozen 100k oracle while bounding memory for fine frontiers.
    routed = []
    for start in range(0, len(x), 4096):
        routed.append(np.argmin(model._boundary_distances(x[start:start + 4096]), axis=1))
    return np.concatenate(routed), model.balls_


def evaluate_tree(family: str, n: int, seed: int, oracle_n: int = 100000) -> list[dict[str, object]]:
    x, y = sample_family(family, n, seed)
    oracle_x, oracle_y = sample_family(family, oracle_n, 100000 + seed)
    rows = []
    tree = XOnlyMaximalGranulationTree(random_state=seed).fit(x).root
    for tau in THRESHOLDS:
        leaves = _cut_geometry(tree, y, tau)
        oracle_route = _route_tree(tree, leaves, oracle_x)
        for ball_id, leaf in enumerate(leaves):
            support = len(leaf.indices); train_purity, label = _purity(leaf, y)
            mask = oracle_route == ball_id; fresh = float((oracle_y[mask] == label).mean()) if mask.any() else float("nan")
            weight = float(mask.mean())
            rows.append({"family":family,"n":n,"seed":seed,"generator":"tree_kmeans_binary","routing":"EXACT_HIERARCHICAL_ROUTING","tau":tau,"ball_id":ball_id,"support":support,"depth":leaf.depth,"train_purity":train_purity,"fresh_reliability":fresh,"optimism":train_purity-fresh,"fresh_weight":weight,"false_high_mass":weight if train_purity>=tau and fresh<tau else 0.0})
    return rows


def evaluate_gbc(family: str, n: int, seed: int, oracle_n: int = 100000) -> list[dict[str, object]]:
    x, y = sample_family(family, n, seed)
    oracle_x, oracle_y = sample_family(family, oracle_n, 100000 + seed)
    rows = []
    for tau in THRESHOLDS:
        model = GranularBallClassifier(purity=tau, random_state=seed).fit(x, y)
        oracle_route, balls = _route_gbc(model, oracle_x)
        for ball_id, ball in enumerate(balls):
            mask = oracle_route == ball_id; fresh = float((oracle_y[mask] == ball.label).mean()) if mask.any() else float("nan"); weight=float(mask.mean())
            rows.append({"family":family,"n":n,"seed":seed,"generator":"gbc_multiclass_cleanroom","routing":"NATIVE_TERMINAL_ROUTING","tau":tau,"ball_id":ball_id,"support":len(ball.members),"depth":None,"train_purity":ball.purity,"fresh_reliability":fresh,"optimism":ball.purity-fresh,"fresh_weight":weight,"false_high_mass":weight if ball.purity>=tau and fresh<tau else 0.0})
    return rows


def evaluate(families=("null_label","smooth_weak","smooth_moderate","piecewise"), sizes=(400,1000), seeds=(1,7,21,42,2026), oracle_n=100000) -> pd.DataFrame:
    rows=[]
    for family in families:
        for n in sizes:
            for seed in seeds:
                rows.extend(evaluate_tree(family,n,seed,oracle_n)); rows.extend(evaluate_gbc(family,n,seed,oracle_n))
    return pd.DataFrame(rows)
