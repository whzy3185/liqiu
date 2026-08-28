"""Strict shadow-to-target A3 discovery on metadata-selected real tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from studies.dataset_mining.approved_loaders import load_approved
from studies.privacy_refinement.a3 import attack_features, gb_release, kmeans_release
from studies.risk_granularity.tree import GranulationTree


DISCOVERY_IDS = ("uci-602", "uci-372", "uci-171")
OUTER_SEEDS = (1, 7, 21)
THRESHOLDS = (0.90, 0.95, 0.99)
LEVELS = ("release_1", "release_2", "release_3")
MAX_POOL = 1200
SHADOW_COUNT = 6
TARGET_COUNT = 5


@dataclass(frozen=True)
class Pool:
    x: np.ndarray
    y: np.ndarray
    seed: int


@dataclass(frozen=True)
class BuiltRelease:
    method: str
    x_features: np.ndarray
    membership: np.ndarray
    number_of_balls: int
    small_ball_ratio: float


def _split_indices(y: np.ndarray, train_size: float | int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=train_size, random_state=seed)
    train, test = next(splitter.split(np.zeros((len(y), 1)), y))
    return train, test


def _cap(indices: np.ndarray, y: np.ndarray, limit: int, seed: int) -> np.ndarray:
    if len(indices) <= limit:
        return indices
    chosen, _ = _split_indices(y[indices], limit, seed)
    return indices[chosen]


def _transform(x: np.ndarray, reference: np.ndarray, indices: np.ndarray) -> np.ndarray:
    imputer = SimpleImputer(strategy="median").fit(reference)
    scaler = StandardScaler().fit(imputer.transform(reference))
    return scaler.transform(imputer.transform(x[indices]))


def _build(pool: Pool, threshold: float, level: str, seed: int) -> tuple[BuiltRelease, BuiltRelease]:
    member, _ = _split_indices(pool.y, .5, seed)
    membership = np.zeros(len(pool.y), dtype=int)
    membership[member] = 1
    x_member, y_member = pool.x[member], pool.y[member]
    tree = GranulationTree(random_state=211 + seed, split_method="kmeans").fit(x_member, y_member)
    gb = gb_release(tree, x_member, threshold, level)
    km = kmeans_release(x_member, y_member, len(gb.members), seed, level)
    def wrap(release) -> BuiltRelease:
        features, _ = attack_features(release, pool.x)
        return BuiltRelease(release.method, features, membership, len(release.members), float((release.sizes <= 2).mean()))
    return wrap(gb), wrap(km)


def _model(attack: str, seed: int):
    if attack == "logistic":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, class_weight="balanced"))
    return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", n_jobs=1, random_state=seed)


def _tpr(y: np.ndarray, score: np.ndarray, fpr_target: float) -> float:
    fpr, tpr, _ = roc_curve(y, score)
    return float(tpr[fpr <= fpr_target].max()) if np.any(fpr <= fpr_target) else 0.0


def _metrics(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    negatives = int((y == 0).sum())
    return {
        "roc_auc": float(roc_auc_score(y, score)),
        "pr_auc": float(average_precision_score(y, score)),
        "tpr_at_1pct_fpr": _tpr(y, score, .01),
        "tpr_at_0_1pct_fpr": _tpr(y, score, .001) if negatives >= 1000 else float("nan"),
    }


def evaluate_dataset(
    source_dataset_id: str,
    root: Path,
    outer_seeds: tuple[int, ...] = OUTER_SEEDS,
    thresholds: tuple[float, ...] = THRESHOLDS,
    levels: tuple[str, ...] = LEVELS,
    shadow_count: int = SHADOW_COUNT,
    target_count: int = TARGET_COUNT,
    max_pool: int = MAX_POOL,
) -> pd.DataFrame:
    x, y, loader_note = load_approved(root, source_dataset_id)
    rows: list[dict[str, object]] = []
    for outer_seed in outer_seeds:
        reference, remaining = _split_indices(y, .20, outer_seed)
        shadow_indices, target_indices = _split_indices(y[remaining], .5, outer_seed + 100)
        shadow_indices = remaining[shadow_indices]
        target_indices = remaining[target_indices]
        shadow_indices = _cap(shadow_indices, y, max_pool, outer_seed + 200)
        target_indices = _cap(target_indices, y, max_pool, outer_seed + 300)
        shadow = Pool(_transform(x, x[reference], shadow_indices), y[shadow_indices], outer_seed)
        target = Pool(_transform(x, x[reference], target_indices), y[target_indices], outer_seed)
        for threshold in thresholds:
            for level in levels:
                shadow_releases = [_build(shadow, threshold, level, outer_seed * 1000 + shadow_id) for shadow_id in range(shadow_count)]
                for target_id in range(target_count):
                    target_releases = _build(target, threshold, level, outer_seed * 10_000 + target_id)
                    for release_index, target_release in enumerate(target_releases):
                        shadows = [pair[release_index] for pair in shadow_releases]
                        x_shadow = np.vstack([release.x_features for release in shadows])
                        y_shadow = np.concatenate([release.membership for release in shadows])
                        for attack in ("logistic", "random_forest"):
                            model = _model(attack, outer_seed * 100 + target_id)
                            model.fit(x_shadow, y_shadow)
                            score = model.predict_proba(target_release.x_features)[:, 1]
                            rows.append({
                                "source_dataset_id": source_dataset_id,
                                "task_id": f"{source_dataset_id}_labeled_train_validation",
                                "parent_dataset": source_dataset_id,
                                "outer_seed": outer_seed,
                                "shadow_release_count": shadow_count,
                                "target_release_id": target_id,
                                "attack_protocol": "real_independent_shadow_target_cross_release",
                                "method": target_release.method,
                                "release": level,
                                "attack": attack,
                                "threshold": threshold,
                                "candidate_pool_size": len(target_release.membership),
                                "negative_count": int((target_release.membership == 0).sum()),
                                "number_of_balls": target_release.number_of_balls,
                                "small_ball_ratio": target_release.small_ball_ratio,
                                "loader_note": loader_note,
                                **_metrics(target_release.membership, score),
                            })
    return pd.DataFrame(rows)
