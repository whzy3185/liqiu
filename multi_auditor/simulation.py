from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit
from sklearn.cluster import KMeans
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from baselines.gbc import GranularBallClassifier


@dataclass(frozen=True)
class AuditorWorld:
    history_truth: np.ndarray
    history_response: np.ndarray
    current_truth: np.ndarray
    current_response: np.ndarray
    features: np.ndarray
    history_accuracy: np.ndarray
    malicious: np.ndarray
    latency: np.ndarray


def generate_world(
    n_auditors: int,
    malicious_ratio: float,
    collusion_strength: float,
    drift: float,
    seed: int,
    n_history: int = 240,
    n_current: int = 300,
) -> AuditorWorld:
    rng = np.random.default_rng(seed)
    n_malicious = max(1, int(round(n_auditors * malicious_ratio)))
    order = rng.permutation(n_auditors)
    malicious_idx = order[:n_malicious]
    adaptive_idx = malicious_idx[: n_malicious // 2]
    malicious = np.zeros(n_auditors, dtype=int)
    malicious[malicious_idx] = 1

    kinds = np.full(n_auditors, "honest", dtype=object)
    remaining = order[n_malicious:]
    kinds[remaining[::4]] = "noisy"
    kinds[remaining[1::5]] = "lazy"
    kinds[malicious_idx] = "malicious"
    kinds[adaptive_idx] = "adaptive"
    history_truth = rng.binomial(1, 0.18, n_history)
    current_truth = rng.binomial(1, 0.18, n_current)
    history_response = np.full((n_history, n_auditors), np.nan)
    current_response = np.full((n_current, n_auditors), np.nan)
    latency = np.zeros(n_auditors)

    shared_attack = 1 - current_truth
    for auditor, kind in enumerate(kinds):
        if kind == "honest":
            history_tpr, history_tnr, coverage, latency[auditor] = 0.92, 0.95, 1.0, rng.uniform(0.7, 1.3)
        elif kind == "noisy":
            history_tpr, history_tnr, coverage, latency[auditor] = 0.72, 0.78, 0.95, rng.uniform(1.0, 2.0)
        elif kind == "lazy":
            history_tpr, history_tnr, coverage, latency[auditor] = 0.86, 0.90, 0.45, rng.uniform(2.0, 4.0)
        elif kind == "adaptive":
            history_tpr, history_tnr, coverage, latency[auditor] = 0.91, 0.94, 1.0, rng.uniform(0.8, 1.5)
        else:
            history_tpr, history_tnr, coverage, latency[auditor] = 0.30, 0.35, 1.0, rng.uniform(0.8, 1.8)
        history_response[:, auditor] = _responses(history_truth, history_tpr, history_tnr, coverage, rng)

        if kind in {"honest", "noisy", "lazy"}:
            current_tpr = max(0.5, history_tpr - drift)
            current_tnr = max(0.5, history_tnr - drift)
            current_response[:, auditor] = _responses(current_truth, current_tpr, current_tnr, coverage, rng)
        else:
            independent = _responses(current_truth, 0.35, 0.35, coverage, rng)
            collude = rng.random(n_current) < collusion_strength
            current_response[:, auditor] = np.where(collude, shared_attack, independent)

    correct = np.where(np.isnan(history_response), np.nan, history_response == history_truth[:, None])
    history_accuracy = np.nanmean(correct, axis=0)
    history_prediction = np.nanmean(history_response, axis=1) >= 0.5
    agreement = np.nanmean(history_response == history_prediction[:, None], axis=0)
    coverage = np.mean(~np.isnan(history_response), axis=0)
    fpr, fnr = [], []
    for auditor in range(n_auditors):
        column = history_response[:, auditor]
        negative = column[history_truth == 0]
        positive = column[history_truth == 1]
        fpr.append(np.nanmean(np.where(np.isnan(negative), np.nan, negative == 1)))
        fnr.append(np.nanmean(np.where(np.isnan(positive), np.nan, positive == 0)))
    target_preference = np.nanmean(current_response, axis=0)
    features = StandardScaler().fit_transform(
        np.column_stack([history_accuracy, fpr, fnr, latency, agreement, coverage, target_preference])
    )
    return AuditorWorld(
        history_truth,
        history_response,
        current_truth,
        current_response,
        features,
        history_accuracy,
        malicious,
        latency,
    )


def evaluate_methods(world: AuditorWorld, seed: int) -> list[dict]:
    methods: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    n = len(world.malicious)
    ones = np.ones(n)
    methods["majority_vote"] = (_aggregate(world.current_response, ones), ones, 0.0)
    beta = (world.history_accuracy * 240 + 1) / 242
    methods["beta_reputation"] = (_aggregate(world.current_response, beta), beta, 0.0)
    weighted = np.maximum(2 * world.history_accuracy - 1, 0.01)
    methods["weighted_majority"] = (_aggregate(world.current_response, weighted), weighted, 0.0)

    ds_probability, ds_competence = _dawid_skene(world.current_response)
    methods["dawid_skene"] = (ds_probability, ds_competence, 0.0)

    gbc = GranularBallClassifier(purity=0.85, min_samples=2, random_state=seed).fit(
        world.features,
        (world.history_accuracy >= 0.75).astype(int),
    )
    gb_weights = np.empty(n)
    for ball in gbc.balls_:
        gb_weights[ball.members] = world.history_accuracy[ball.members].mean()
    k = len(gbc.balls_)
    km_assignment = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(world.features)
    km_weights = _group_score(world.history_accuracy, km_assignment)
    if k == 1:
        tree_weights = np.full(n, world.history_accuracy.mean())
    else:
        tree_weights = DecisionTreeRegressor(
            max_leaf_nodes=k,
            min_samples_leaf=2,
            random_state=seed,
        ).fit(world.features, world.history_accuracy).predict(world.features)
    knn_weights = KNeighborsRegressor(n_neighbors=min(5, n), weights="distance").fit(
        world.features, world.history_accuracy
    ).predict(world.features)
    methods["kmeans_trust"] = (_aggregate(world.current_response, km_weights), km_weights, 0.0)
    methods["tree_partition"] = (_aggregate(world.current_response, tree_weights), tree_weights, 0.0)
    methods["knn_competence"] = (_aggregate(world.current_response, knn_weights), knn_weights, 0.0)
    methods["granular_ball"] = (_aggregate(world.current_response, gb_weights), gb_weights, 0.0)

    tiers = np.where(gb_weights >= 0.8, 1.0, np.where(gb_weights >= 0.6, 0.4, 0.0))
    uncertain_ratio = float(np.mean((gb_weights >= 0.6) & (gb_weights < 0.8)))
    methods["gb_three_way"] = (
        _aggregate(world.current_response, np.maximum(tiers, 0.01)),
        tiers,
        uncertain_ratio * len(world.current_truth),
    )

    rows = []
    honest = world.malicious == 0
    for method, (probability, trust, extra_cost) in methods.items():
        prediction = probability >= 0.5
        malicious_score = -trust
        rows.append(
            {
                "method": method,
                "n_groups": k if method in {"kmeans_trust", "tree_partition", "granular_ball", "gb_three_way"} else None,
                "metrics": {
                    "final_audit_accuracy": float(np.mean(prediction == world.current_truth)),
                    "malicious_auroc": _safe_roc(world.malicious, malicious_score),
                    "malicious_auprc": float(average_precision_score(world.malicious, malicious_score)),
                    "false_trust_rate": float(np.mean(trust[world.malicious == 1] >= 0.75)),
                    "false_rejection_rate": float(np.mean(trust[honest] < 0.5)),
                    "additional_audit_cost": float(extra_cost),
                    "decision_delay": float(np.mean(world.latency[trust > 0.1])) if np.any(trust > 0.1) else float(world.latency.max()),
                },
            }
        )
    return rows


def _responses(truth: np.ndarray, tpr: float, tnr: float, coverage: float, rng) -> np.ndarray:
    probability = np.where(truth == 1, tpr, 1 - tnr)
    result = (rng.random(len(truth)) < probability).astype(float)
    result[rng.random(len(truth)) > coverage] = np.nan
    return result


def _aggregate(matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
    observed = ~np.isnan(matrix)
    numerator = np.nansum(matrix * weights[None, :], axis=1)
    denominator = np.sum(observed * weights[None, :], axis=1)
    return np.divide(numerator, denominator, out=np.full(len(matrix), 0.5), where=denominator > 0)


def _group_score(values: np.ndarray, assignment: np.ndarray) -> np.ndarray:
    result = np.empty(len(values))
    for group in np.unique(assignment):
        mask = assignment == group
        result[mask] = values[mask].mean()
    return result


def _dawid_skene(matrix: np.ndarray, iterations: int = 15) -> tuple[np.ndarray, np.ndarray]:
    observed = ~np.isnan(matrix)
    probability = np.nanmean(matrix, axis=1)
    probability = np.nan_to_num(probability, nan=0.5)
    eps = 1e-4
    for _ in range(iterations):
        positive_weight = probability[:, None] * observed
        negative_weight = (1 - probability)[:, None] * observed
        sensitivity = np.sum(positive_weight * np.nan_to_num(matrix), axis=0) / np.maximum(positive_weight.sum(axis=0), eps)
        specificity = np.sum(negative_weight * (1 - np.nan_to_num(matrix)), axis=0) / np.maximum(negative_weight.sum(axis=0), eps)
        sensitivity = np.clip(sensitivity, 0.51, 0.99)
        specificity = np.clip(specificity, 0.51, 0.99)
        prior = np.clip(probability.mean(), 0.01, 0.99)
        log_odds = np.full(len(matrix), np.log(prior / (1 - prior)))
        for auditor in range(matrix.shape[1]):
            yes = matrix[:, auditor] == 1
            no = matrix[:, auditor] == 0
            log_odds[yes] += np.log(sensitivity[auditor] / (1 - specificity[auditor]))
            log_odds[no] += np.log((1 - sensitivity[auditor]) / specificity[auditor])
        probability = expit(log_odds)
    return probability, (sensitivity + specificity) / 2


def _safe_roc(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score)) if len(np.unique(y)) == 2 else 0.5
