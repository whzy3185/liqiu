"""Synthetic-oracle adaptive purity validity audit (frozen v1 definitions)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from baselines.gbc import GranularBallClassifier
from studies.risk_granularity.tree import GranulationTree


THRESHOLDS = (.70, .80, .90, .95, .99, 1.0)


def sample_family(name: str, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    modes = rng.integers(0, 4, n)
    centers = np.array([[-2, -2], [-2, 2], [2, -2], [2, 2]], float)
    x = centers[modes] + rng.normal(0, .9, (n, 2))
    if name == "null":
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


def _route_tree(tree, x: np.ndarray, tau: float) -> tuple[np.ndarray, list]:
    leaves = tree.cut(tau)
    ids = {id(node): index for index, node in enumerate(leaves)}
    routed = []
    for row in x:
        node = tree.root
        while id(node) not in ids:
            node = node.children[int(np.argmin([np.linalg.norm(row - child.center) for child in node.children]))]
        routed.append(ids[id(node)])
    return np.asarray(routed), leaves


def _route_gbc(model, x: np.ndarray) -> tuple[np.ndarray, list]:
    distances = model._boundary_distances(x)
    return np.argmin(distances, axis=1), model.balls_


def evaluate_tree(family: str, n: int, seed: int, oracle_n: int = 100000) -> list[dict[str, object]]:
    x, y = sample_family(family, n, seed)
    oracle_x, oracle_y = sample_family(family, oracle_n, 100000 + seed)
    rows = []
    tree = GranulationTree(random_state=seed, split_method="kmeans").fit(x, y)
    for tau in THRESHOLDS:
        oracle_route, leaves = _route_tree(tree, oracle_x, tau)
        for ball_id, leaf in enumerate(leaves):
            support = len(leaf.indices); label = leaf.label; train_purity = leaf.purity
            mask = oracle_route == ball_id; fresh = float((oracle_y[mask] == label).mean()) if mask.any() else float("nan")
            weight = float(mask.mean())
            rows.append({"family":family,"n":n,"seed":seed,"generator":"tree_kmeans_binary","routing":"EXACT_HIERARCHICAL_ROUTING","tau":tau,"ball_id":ball_id,"support":support,"depth":None,"train_purity":train_purity,"fresh_reliability":fresh,"optimism":train_purity-fresh,"fresh_weight":weight,"false_high_mass":weight if train_purity>=tau and fresh<tau else 0.0})
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


def evaluate(families=("null","smooth_weak","smooth_moderate","piecewise"), sizes=(400,1000), seeds=(1,7,21,42,2026), oracle_n=100000) -> pd.DataFrame:
    rows=[]
    for family in families:
        for n in sizes:
            for seed in seeds:
                rows.extend(evaluate_tree(family,n,seed,oracle_n)); rows.extend(evaluate_gbc(family,n,seed,oracle_n))
    return pd.DataFrame(rows)
