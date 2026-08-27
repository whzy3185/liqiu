"""Strict shadow-to-target membership attacks for the frozen A3 regime."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from studies.privacy_refinement.a3 import (
    attack_features,
    attack_metrics,
    gb_release,
    kmeans_release,
    synthetic_regime,
)
from studies.risk_granularity.tree import GranulationTree


CONFIRMATION_POINTS = (
    {"dimension": 60, "redundant_fraction": 0.0, "label_noise": 0.05},
    {"dimension": 60, "redundant_fraction": 0.1, "label_noise": 0.15},
    {"dimension": 100, "redundant_fraction": 0.0, "label_noise": 0.05},
    {"dimension": 100, "redundant_fraction": 0.1, "label_noise": 0.15},
)
THRESHOLDS = (0.90, 0.95, 0.99)
SHADOW_SEEDS = tuple(range(1001, 1013))
TARGET_SEEDS = tuple(range(2001, 2009))


@dataclass(frozen=True)
class CandidatePool:
    x: np.ndarray
    clean_y: np.ndarray
    noisy_y: np.ndarray
    pool_seed: int


@dataclass(frozen=True)
class ConstructedRelease:
    method: str
    release: str
    threshold: float
    pool_seed: int
    member_seed: int
    features: np.ndarray
    membership: np.ndarray
    number_of_balls: int
    small_ball_ratio: float
    member_x: np.ndarray
    nonmember_x: np.ndarray


def _flip_labels(y: np.ndarray, fraction: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    result = y.copy()
    positions = rng.choice(len(y), size=int(round(len(y) * fraction)), replace=False)
    classes = np.unique(y)
    for position in positions:
        result[position] = rng.choice(classes[classes != result[position]])
    return result


def candidate_pool(params: dict[str, object], pool_seed: int) -> CandidatePool:
    clean_x, clean_y = synthetic_regime(
        n=600,
        dimension=int(params["dimension"]),
        separation=2.0,
        density_ratio=5.0,
        minority_fraction=0.30,
        modes=3,
        redundant_fraction=float(params["redundant_fraction"]),
        label_noise=0.0,
        seed=pool_seed,
    )
    noisy_y = _flip_labels(clean_y, float(params["label_noise"]), pool_seed * 37 + 11)
    return CandidatePool(clean_x, clean_y, noisy_y, pool_seed)


def external_scaler(params: dict[str, object]) -> StandardScaler:
    x, _ = synthetic_regime(
        n=1200,
        dimension=int(params["dimension"]),
        separation=2.0,
        density_ratio=5.0,
        minority_fraction=0.30,
        modes=3,
        redundant_fraction=float(params["redundant_fraction"]),
        label_noise=0.0,
        seed=900_000 + int(params["dimension"]) * 10 + int(round(float(params["label_noise"]) * 100)),
    )
    return StandardScaler().fit(x)


def member_indices(clean_y: np.ndarray, seed: int) -> np.ndarray:
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=0.5, random_state=seed)
    members, _ = next(splitter.split(np.zeros((len(clean_y), 1)), clean_y))
    return members


def construct(pool: CandidatePool, scaler: StandardScaler, member_seed: int, threshold: float, release_level: str) -> tuple[ConstructedRelease, ConstructedRelease]:
    x = scaler.transform(pool.x)
    members = member_indices(pool.clean_y, member_seed)
    membership = np.zeros(len(x), dtype=int)
    membership[members] = 1
    nonmembers = np.flatnonzero(membership == 0)
    member_x, member_y = x[members], pool.noisy_y[members]
    tree = GranulationTree(random_state=211 + member_seed, split_method="kmeans").fit(member_x, member_y)
    gb = gb_release(tree, member_x, threshold, release_level)
    km = kmeans_release(member_x, member_y, len(gb.members), member_seed, release_level)
    def wrap(release) -> ConstructedRelease:
        features, _ = attack_features(release, x)
        return ConstructedRelease(
            release.method,
            release_level,
            threshold,
            pool.pool_seed,
            member_seed,
            features,
            membership,
            len(release.members),
            float((release.sizes <= 2).mean()),
            member_x,
            x[nonmembers],
        )
    return wrap(gb), wrap(km)


def _tpr(y: np.ndarray, score: np.ndarray, target: float) -> float:
    fpr, tpr, _ = roc_curve(y, score)
    return float(tpr[fpr <= target].max()) if np.any(fpr <= target) else 0.0


def _model(attack: str, seed: int):
    if attack == "logistic":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, class_weight="balanced"))
    return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", n_jobs=1, random_state=seed)


def metrics(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    negatives = int((y == 0).sum())
    return {
        "roc_auc": float(roc_auc_score(y, score)),
        "pr_auc": float(average_precision_score(y, score)),
        "tpr_at_1pct_fpr": _tpr(y, score, .01),
        "tpr_at_0_1pct_fpr": _tpr(y, score, .001) if negatives >= 1000 else float("nan"),
    }


def _strict_scores(shadows: list[ConstructedRelease], target: ConstructedRelease, attack: str, seed: int) -> np.ndarray:
    x_shadow = np.vstack([release.features for release in shadows])
    y_shadow = np.concatenate([release.membership for release in shadows])
    model = _model(attack, seed)
    model.fit(x_shadow, y_shadow)
    return model.predict_proba(target.features)[:, 1]


def _same_release_scores(target: ConstructedRelease, attack: str, seed: int) -> np.ndarray:
    # Diagnostic only: mirrors the prior same-release candidate-level CV protocol.
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    model = _model(attack, seed)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    return cross_val_predict(model, target.features, target.membership, cv=cv, method="predict_proba", n_jobs=1)[:, 1]


def _row(params: dict[str, object], protocol: str, shadow_seed: int | str, target_seed: int, release: ConstructedRelease, attack: str, score: np.ndarray) -> dict[str, object]:
    return {
        "generator_regime": f"d{params['dimension']}_redundancy{params['redundant_fraction']}_noise{params['label_noise']}",
        "shadow_seed": shadow_seed,
        "target_seed": target_seed,
        "attack_protocol": protocol,
        "method": release.method,
        "release": release.release,
        "attack": attack,
        "threshold": release.threshold,
        "number_of_balls": release.number_of_balls,
        "small_ball_ratio": release.small_ball_ratio,
        "candidate_count": len(release.membership),
        "negative_count": int((release.membership == 0).sum()),
        **metrics(release.membership, score),
        **params,
    }


def run_validity(
    points: tuple[dict[str, object], ...] = CONFIRMATION_POINTS,
    thresholds: tuple[float, ...] = THRESHOLDS,
    levels: tuple[str, ...] = ("release_1", "release_2", "release_3"),
    shadow_seeds: tuple[int, ...] = SHADOW_SEEDS,
    target_seeds: tuple[int, ...] = TARGET_SEEDS,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for point_id, params in enumerate(points):
        scaler = external_scaler(params)
        shadow_pools = [candidate_pool(params, 10_000 * (point_id + 1) + seed) for seed in shadow_seeds]
        target_pools = [candidate_pool(params, 20_000 * (point_id + 1) + seed) for seed in target_seeds]
        fixed_pool = candidate_pool(params, 30_000 * (point_id + 1) + 1)
        for threshold in thresholds:
            for level in levels:
                independent_shadows = [construct(pool, scaler, pool.pool_seed + 71, threshold, level) for pool in shadow_pools]
                fixed_shadows = [construct(fixed_pool, scaler, seed, threshold, level) for seed in shadow_seeds]
                for target_pool in target_pools:
                    independent_target = construct(target_pool, scaler, target_pool.pool_seed + 71, threshold, level)
                    for release_index, target in enumerate(independent_target):
                        shadows = [pair[release_index] for pair in independent_shadows]
                        for attack in ("logistic", "random_forest"):
                            strict = _strict_scores(shadows, target, attack, target_pool.pool_seed)
                            rows.append(_row(params, "independent_pool_cross_release", "independent_suite", target_pool.pool_seed, target, attack, strict))
                            same = _same_release_scores(target, attack, target_pool.pool_seed)
                            rows.append(_row(params, "same_release_cv", "not_applicable", target_pool.pool_seed, target, attack, same))
                for target_seed in target_seeds:
                    fixed_target = construct(fixed_pool, scaler, target_seed, threshold, level)
                    for release_index, target in enumerate(fixed_target):
                        shadows = [pair[release_index] for pair in fixed_shadows]
                        for attack in ("logistic", "random_forest"):
                            strict = _strict_scores(shadows, target, attack, target_seed)
                            rows.append(_row(params, "fixed_noise_same_pool_cross_release", "fixed_pool_suite", target_seed, target, attack, strict))
    return pd.DataFrame(rows)
