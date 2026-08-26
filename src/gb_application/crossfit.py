"""Cross-fitted supervised granular features for training and held-out data."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.model_selection import StratifiedKFold

from .features import structural_features
from .generator import StableGranularBallGenerator


@dataclass(frozen=True)
class FoldAudit:
    fold: int
    fit_indices: tuple[int, ...]
    query_indices: tuple[int, ...]
    n_balls: int


@dataclass(frozen=True)
class CrossFittedGBFeatures:
    train: np.ndarray
    validation: np.ndarray
    test: np.ndarray
    audits: tuple[FoldAudit, ...]
    full_generator: StableGranularBallGenerator


def cross_fitted_gb_features(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_validation: np.ndarray,
    X_test: np.ndarray,
    *,
    seed: int,
    n_splits: int = 5,
    purity: float = 0.9,
    min_samples: int = 5,
    max_balls: int = 256,
) -> CrossFittedGBFeatures:
    X_train = np.asarray(X_train, dtype=float)
    y_train = np.asarray(y_train).reshape(-1)
    minimum_class = min(int(np.sum(y_train == label)) for label in np.unique(y_train))
    effective_splits = min(n_splits, minimum_class)
    if effective_splits < 2:
        raise ValueError("cross-fitting requires at least two samples in every class")
    splitter = StratifiedKFold(n_splits=effective_splits, shuffle=True, random_state=seed)
    out_of_fold = np.empty((len(X_train), 12), dtype=float)
    audits: list[FoldAudit] = []
    for fold, (fit_indices, query_indices) in enumerate(splitter.split(X_train, y_train)):
        generator = StableGranularBallGenerator(
            purity=purity,
            min_samples=min_samples,
            random_state=seed + fold,
            max_balls=max_balls,
        ).fit(X_train[fit_indices], y_train[fit_indices])
        out_of_fold[query_indices], _ = structural_features(generator, X_train[query_indices])
        audits.append(
            FoldAudit(
                fold=fold,
                fit_indices=tuple(int(value) for value in fit_indices),
                query_indices=tuple(int(value) for value in query_indices),
                n_balls=len(generator.balls_),
            )
        )
    full_generator = StableGranularBallGenerator(
        purity=purity,
        min_samples=min_samples,
        random_state=seed,
        max_balls=max_balls,
    ).fit(X_train, y_train)
    validation, _ = structural_features(full_generator, X_validation)
    test, _ = structural_features(full_generator, X_test)
    return CrossFittedGBFeatures(
        train=out_of_fold,
        validation=validation,
        test=test,
        audits=tuple(audits),
        full_generator=full_generator,
    )

