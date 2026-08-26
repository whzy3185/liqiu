"""Fixed-budget conventional ML baselines shared by raw and GB experiments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier


@dataclass(frozen=True)
class ModelSpec:
    name: str
    estimator: Any
    fit_cap: int | None = None


def conventional_models(
    seed: int,
    n_classes: int,
    *,
    class_counts: dict[int, int] | None = None,
    diagnostic_cap: int = 5_000,
) -> list[ModelSpec]:
    binary = n_classes == 2
    class_counts = class_counts or {}
    if binary and set(class_counts) == {0, 1} and class_counts[1] > 0:
        positive_weight = float(class_counts[0] / class_counts[1])
    else:
        positive_weight = 1.0
    xgb_objective = "binary:logistic" if binary else "multi:softprob"
    xgb_metric = "logloss" if binary else "mlogloss"
    return [
        ModelSpec(
            "xgboost",
            XGBClassifier(
                n_estimators=220,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                min_child_weight=2,
                reg_lambda=1.0,
                objective=xgb_objective,
                eval_metric=xgb_metric,
                n_jobs=-1,
                random_state=seed,
                tree_method="hist",
                scale_pos_weight=positive_weight,
            ),
        ),
        ModelSpec(
            "lightgbm",
            LGBMClassifier(
                n_estimators=220,
                num_leaves=31,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_lambda=1.0,
                n_jobs=-1,
                random_state=seed,
                verbosity=-1,
                class_weight="balanced",
            ),
        ),
        ModelSpec(
            "catboost",
            CatBoostClassifier(
                iterations=220,
                depth=6,
                learning_rate=0.05,
                l2_leaf_reg=3.0,
                random_seed=seed,
                verbose=False,
                allow_writing_files=False,
                thread_count=-1,
                auto_class_weights="Balanced",
            ),
        ),
        ModelSpec(
            "random_forest",
            RandomForestClassifier(
                n_estimators=300,
                max_features="sqrt",
                min_samples_leaf=1,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=seed,
            ),
        ),
        ModelSpec(
            "extra_trees",
            ExtraTreesClassifier(
                n_estimators=300,
                max_features="sqrt",
                min_samples_leaf=1,
                class_weight="balanced",
                n_jobs=-1,
                random_state=seed,
            ),
        ),
        ModelSpec("knn", KNeighborsClassifier(n_neighbors=7, weights="distance", n_jobs=-1), diagnostic_cap),
        ModelSpec(
            "svm_rbf",
            SVC(C=3.0, gamma="scale", class_weight="balanced", cache_size=2048),
            diagnostic_cap,
        ),
    ]


def capped_fit_indices(y: np.ndarray, cap: int | None, seed: int) -> np.ndarray:
    if cap is None or len(y) <= cap:
        return np.arange(len(y))
    rng = np.random.default_rng(seed)
    selected: list[int] = []
    for label in np.unique(y):
        indices = np.flatnonzero(y == label)
        quota = max(1, int(round(cap * len(indices) / len(y))))
        selected.extend(rng.choice(indices, size=min(quota, len(indices)), replace=False).tolist())
    if len(selected) > cap:
        selected = rng.choice(selected, size=cap, replace=False).tolist()
    return np.asarray(sorted(selected), dtype=int)
