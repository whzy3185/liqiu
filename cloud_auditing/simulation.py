from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from baselines.gbc import GranularBallClassifier


@dataclass(frozen=True)
class CloudBlocks:
    X: np.ndarray
    raw: dict[str, np.ndarray]
    historical_event: np.ndarray
    generic_risk: np.ndarray


def generate_blocks(n: int, seed: int) -> CloudBlocks:
    rng = np.random.default_rng(seed)
    raw = {
        "age": rng.exponential(2.0, n),
        "access": rng.lognormal(1.0, 1.0, n),
        "updates": rng.poisson(1.5, n).astype(float),
        "node": rng.integers(0, 50, n),
        "file_type": rng.integers(0, 6, n),
        "importance": rng.beta(2, 3, n),
        "anomaly": rng.exponential(0.7, n),
    }
    node_effect = rng.normal(0, 0.45, 50)[raw["node"]]
    latent = (
        0.35 * np.log1p(raw["age"])
        - 0.25 * np.log1p(raw["access"])
        + 0.25 * raw["updates"]
        + 0.9 * raw["importance"]
        + 0.8 * np.log1p(raw["anomaly"])
        + node_effect
        - 3.7
    )
    generic_risk = np.clip(expit(latent), 1e-4, 0.5)
    history_count = rng.binomial(12, generic_risk)
    historical_event = (history_count > 0).astype(int)
    raw["historical_failures"] = history_count.astype(float)

    continuous = np.column_stack(
        [
            np.log1p(raw["age"]),
            np.log1p(raw["access"]),
            raw["updates"],
            raw["historical_failures"],
            raw["importance"],
            np.log1p(raw["anomaly"]),
        ]
    )
    encoder = OneHotEncoder(sparse_output=False)
    categories = encoder.fit_transform(np.column_stack([raw["node"], raw["file_type"]]))
    X = np.column_stack([StandardScaler().fit_transform(continuous), categories])
    return CloudBlocks(X=X, raw=raw, historical_event=historical_event, generic_risk=generic_risk)


def audit_policies(blocks: CloudBlocks, seed: int, fit_cap: int = 5000) -> tuple[dict[str, np.ndarray], int]:
    X, history = blocks.X, blocks.historical_event
    rng = np.random.default_rng(seed)
    fit_idx = rng.choice(len(X), size=min(fit_cap, len(X)), replace=False)
    risk_model = LogisticRegression(max_iter=500, class_weight="balanced").fit(X[fit_idx], history[fit_idx])
    risk_score = risk_model.predict_proba(X)[:, 1]
    high_risk = (risk_score[fit_idx] >= np.quantile(risk_score[fit_idx], 0.7)).astype(int)
    gbc = GranularBallClassifier(purity=0.85, min_samples=5, random_state=seed).fit(X[fit_idx], high_risk)
    gb_assignment = _assign_gb(X, gbc)
    k = len(gbc.balls_)

    kmeans = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X[fit_idx])
    km_assignment = kmeans.predict(X)
    tree = DecisionTreeRegressor(
        max_leaf_nodes=k,
        min_samples_leaf=max(10, len(fit_idx) // max(4 * k, 1)),
        random_state=seed,
    ).fit(X[fit_idx], risk_score[fit_idx])

    gb_group = _group_mean(risk_score, gb_assignment, k)
    km_group = _group_mean(risk_score, km_assignment, k)
    gb_center_score = risk_model.predict_proba(np.vstack([ball.center for ball in gbc.balls_]))[:, 1]
    q_low, q_high = np.quantile(gb_group, [1 / 3, 2 / 3])
    tier_multiplier = np.where(gb_group <= q_low, 0.5, np.where(gb_group >= q_high, 2.0, 1.0))

    hand_weight = (
        1.0
        + blocks.raw["historical_failures"]
        + blocks.raw["importance"]
        + np.log1p(blocks.raw["anomaly"])
    )
    policies = {
        "uniform": np.ones(len(X)),
        "weighted_random": hand_weight,
        "risk_score": risk_score,
        "anomaly_score": 1e-6 + blocks.raw["anomaly"],
        "kmeans_group": km_group[km_assignment],
        "tree_partition": np.maximum(tree.predict(X), 1e-6),
        "gb_center_only": gb_center_score[gb_assignment],
        "granular_ball": gb_group[gb_assignment],
        "gb_three_way": (gb_group * tier_multiplier)[gb_assignment],
    }
    return {name: _normalize(score) for name, score in policies.items()}, k


def corruption_indices(
    blocks: CloudBlocks,
    scenario: str,
    n_corrupt: int,
    seed: int,
    policy: np.ndarray | None = None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = blocks.raw
    if scenario == "uniform":
        weights = np.ones(len(blocks.X))
    elif scenario == "clustered":
        nodes = rng.choice(50, size=2, replace=False)
        file_type = int(rng.integers(0, 6))
        weights = 1.0 + 30.0 * (np.isin(raw["node"], nodes) & (raw["file_type"] == file_type))
    elif scenario == "hot_targeted":
        weights = (1.0 + raw["access"]) * (0.25 + raw["importance"])
    elif scenario == "cold_targeted":
        weights = (1.0 + raw["age"]) / (1.0 + raw["access"])
    elif scenario == "adversarial":
        if policy is None:
            raise ValueError("adversarial corruption requires the audited policy")
        cutoff = np.quantile(policy, 0.2)
        weights = (policy <= cutoff).astype(float)
    else:
        raise ValueError(scenario)
    weights = _normalize(weights)
    return rng.choice(len(blocks.X), size=n_corrupt, replace=False, p=weights)


def evaluate_policy(
    policy: np.ndarray,
    corrupted: np.ndarray,
    budget: int,
    seed: int,
    repeats: int = 30,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    corrupted_mask = np.zeros(len(policy), dtype=bool)
    corrupted_mask[corrupted] = True
    any_detected, first, recall, miss = [], [], [], []
    for _ in range(repeats):
        audited = rng.choice(len(policy), size=budget, replace=False, p=policy)
        hits = corrupted_mask[audited]
        positions = np.flatnonzero(hits)
        any_detected.append(bool(len(positions)))
        first.append(float(positions[0] + 1) if len(positions) else float(budget + 1))
        recall.append(float(hits.sum() / len(corrupted)))
        miss.append(1.0 - recall[-1])
    return {
        "detection_probability": float(np.mean(any_detected)),
        "time_to_first_detection": float(np.mean(first)),
        "corruption_recall": float(np.mean(recall)),
        "audit_cost": float(budget),
        "worst_case_miss_rate": float(np.quantile(miss, 0.95)),
    }


def _group_mean(values: np.ndarray, assignments: np.ndarray, k: int) -> np.ndarray:
    totals = np.bincount(assignments, weights=values, minlength=k)
    counts = np.bincount(assignments, minlength=k)
    fallback = float(values.mean())
    return np.divide(totals, counts, out=np.full(k, fallback), where=counts > 0)


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.maximum(np.asarray(values, dtype=float), 1e-12)
    return values / values.sum()


def _assign_gb(X: np.ndarray, gbc: GranularBallClassifier, chunk_size: int = 10_000) -> np.ndarray:
    centers = np.vstack([ball.center for ball in gbc.balls_])
    radii = np.asarray([ball.radius for ball in gbc.balls_])
    assignment = np.empty(len(X), dtype=int)
    for start in range(0, len(X), chunk_size):
        stop = min(start + chunk_size, len(X))
        distances = pairwise_distances(X[start:stop], centers) - radii[None, :]
        assignment[start:stop] = np.argmin(distances, axis=1)
    return assignment
