"""Group-disjoint strict A3 discovery for the MicroMass pure-reference task."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from studies.dataset_mining.approved_loaders import load_approved_grouped
from studies.privacy_refinement.a3 import Release, attack_features, gb_release, kmeans_release
from studies.privacy_refinement.a3_real_strict import _metrics, _model
from studies.risk_granularity.tree import GranulationTree


SOURCE_DATASET_ID = "uci-253"
OUTER_SEEDS = (1, 7, 21)
THRESHOLDS = (0.90, 0.95, 0.99)
LEVELS = ("release_1", "release_2", "release_3")
SHADOW_COUNT = 6
TARGET_COUNT = 5


@dataclass(frozen=True)
class GroupPool:
    x: np.ndarray
    y: np.ndarray
    groups: np.ndarray


@dataclass(frozen=True)
class BuiltRelease:
    method: str
    x_features: np.ndarray
    membership: np.ndarray
    number_of_balls: int
    small_ball_ratio: float


def _class_group_partition(y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Make external-reference, shadow, and target pools disjoint by strain.

    Partitioning occurs inside each species.  Every class has at least seven
    strains, so each of the three pools retains every species before an attack
    result is observed.
    """
    rng = np.random.default_rng(seed)
    reference_groups: list[str] = []
    shadow_groups: list[str] = []
    target_groups: list[str] = []
    for label in np.unique(y):
        class_groups = np.unique(groups[y == label]).astype(str)
        if len(class_groups) < 5:
            raise ValueError(f"class {label} has too few strains for the frozen protocol: {len(class_groups)}")
        shuffled = rng.permutation(class_groups)
        reference_count = max(1, int(round(.20 * len(shuffled))))
        remaining = len(shuffled) - reference_count
        shadow_count = remaining // 2
        target_count = remaining - shadow_count
        if shadow_count < 2 or target_count < 2:
            raise ValueError(f"class {label} cannot support group-disjoint member/nonmember splits")
        reference_groups.extend(shuffled[:reference_count])
        shadow_groups.extend(shuffled[reference_count:reference_count + shadow_count])
        target_groups.extend(shuffled[reference_count + shadow_count:])
    return np.asarray(reference_groups), np.asarray(shadow_groups), np.asarray(target_groups)


def _group_member_mask(y: np.ndarray, groups: np.ndarray, seed: int) -> np.ndarray:
    """Choose membership by strain, stratified within species."""
    rng = np.random.default_rng(seed)
    member_groups: list[str] = []
    for label in np.unique(y):
        class_groups = rng.permutation(np.unique(groups[y == label]).astype(str))
        if len(class_groups) < 2:
            raise ValueError(f"class {label} lacks two strains inside an attack pool")
        member_groups.extend(class_groups[: len(class_groups) // 2])
    mask = np.isin(groups.astype(str), np.asarray(member_groups))
    if set(groups[mask]) & set(groups[~mask]):
        raise RuntimeError("strain leaked across member/nonmember groups")
    return mask


def _transform(x: np.ndarray, reference: np.ndarray, indices: np.ndarray) -> np.ndarray:
    imputer = SimpleImputer(strategy="median").fit(reference)
    scaler = StandardScaler().fit(imputer.transform(reference))
    return scaler.transform(imputer.transform(x[indices]))


def _as_pool(x: np.ndarray, y: np.ndarray, groups: np.ndarray, indices: np.ndarray, reference: np.ndarray) -> GroupPool:
    return GroupPool(_transform(x, reference, indices), y[indices], groups[indices])


def _build(pool: GroupPool, threshold: float, seed: int, vocabulary: np.ndarray) -> dict[str, tuple[BuiltRelease, BuiltRelease]]:
    member = _group_member_mask(pool.y, pool.groups, seed)
    membership = member.astype(int)
    x_member, y_member = pool.x[member], pool.y[member]
    tree = GranulationTree(random_state=211 + seed, split_method="kmeans").fit(x_member, y_member)
    gb_base = gb_release(tree, x_member, threshold, "release_1")
    km_base = kmeans_release(x_member, y_member, len(gb_base.members), seed, "release_1")

    def wrap(release: Release) -> BuiltRelease:
        features, _ = attack_features(release, pool.x, label_vocabulary=vocabulary)
        return BuiltRelease(
            method=release.method,
            x_features=features,
            membership=membership,
            number_of_balls=len(release.members),
            small_ball_ratio=float((release.sizes <= 2).mean()),
        )

    return {
        level: (wrap(replace(gb_base, level=level)), wrap(replace(km_base, level=level)))
        for level in LEVELS
    }


def _validate_partition(reference: np.ndarray, shadow: np.ndarray, target: np.ndarray) -> None:
    if set(reference) & set(shadow) or set(reference) & set(target) or set(shadow) & set(target):
        raise RuntimeError("strain leaked across reference/shadow/target pools")


def evaluate_micromass(
    root: Path,
    outer_seeds: tuple[int, ...] = OUTER_SEEDS,
    thresholds: tuple[float, ...] = THRESHOLDS,
    shadow_count: int = SHADOW_COUNT,
    target_count: int = TARGET_COUNT,
) -> pd.DataFrame:
    x, y, groups, loader_note = load_approved_grouped(root, SOURCE_DATASET_ID)
    vocabulary = np.unique(y)
    rows: list[dict[str, object]] = []
    for outer_seed in outer_seeds:
        reference_groups, shadow_groups, target_groups = _class_group_partition(y, groups, outer_seed)
        _validate_partition(reference_groups, shadow_groups, target_groups)
        reference_indices = np.flatnonzero(np.isin(groups, reference_groups))
        shadow_indices = np.flatnonzero(np.isin(groups, shadow_groups))
        target_indices = np.flatnonzero(np.isin(groups, target_groups))
        reference = x[reference_indices]
        shadow = _as_pool(x, y, groups, shadow_indices, reference)
        target = _as_pool(x, y, groups, target_indices, reference)
        for threshold in thresholds:
            shadow_releases = [_build(shadow, threshold, outer_seed * 1_000 + shadow_id, vocabulary) for shadow_id in range(shadow_count)]
            for target_id in range(target_count):
                target_releases = _build(target, threshold, outer_seed * 10_000 + target_id, vocabulary)
                for level in LEVELS:
                    for release_index, target_release in enumerate(target_releases[level]):
                        shadows = [release[level][release_index] for release in shadow_releases]
                        x_shadow = np.vstack([release.x_features for release in shadows])
                        y_shadow = np.concatenate([release.membership for release in shadows])
                        for attack in ("logistic", "random_forest"):
                            model = _model(attack, outer_seed * 100 + target_id)
                            model.fit(x_shadow, y_shadow)
                            score = model.predict_proba(target_release.x_features)[:, 1]
                            rows.append({
                                "source_dataset_id": SOURCE_DATASET_ID,
                                "task_id": "micromass_pure_species",
                                "parent_dataset": "MicroMass",
                                "outer_seed": outer_seed,
                                "shadow_release_count": shadow_count,
                                "target_release_id": target_id,
                                "attack_protocol": "real_strain_disjoint_reference_shadow_target_and_membership_cross_release",
                                "method": target_release.method,
                                "release": level,
                                "attack": attack,
                                "threshold": threshold,
                                "candidate_pool_size": len(target_release.membership),
                                "negative_count": int((target_release.membership == 0).sum()),
                                "reference_group_count": len(reference_groups),
                                "shadow_group_count": len(shadow_groups),
                                "target_group_count": len(target_groups),
                                "number_of_balls": target_release.number_of_balls,
                                "small_ball_ratio": target_release.small_ball_ratio,
                                "loader_note": loader_note,
                                **_metrics(target_release.membership, score),
                            })
    return pd.DataFrame(rows)
