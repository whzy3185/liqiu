"""Pre-frozen independent confirmation for structural/predictive decoupling."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import StratifiedShuffleSplit

from studies.privacy_refinement.a3 import load_dataset
from studies.structural_stability.cheap_test import (
    GENERATORS, TRAIN_CAP, TEST_CAP, _delete_indices, _fit_structure,
    _flip_labels, _nearest_center_predict, _partition_metrics, _subsample,
    _transform_fit,
)


DATASETS = ("iris", "sonar", "spambase")
SCENARIOS = (("label_flip", .05), ("sample_deletion", .01))
SEEDS = (101, 313, 911)


def _load(name: str) -> tuple[np.ndarray, np.ndarray, str]:
    if name == "iris":
        data = load_iris()
        return np.asarray(data.data, float), np.asarray(data.target, int), "sklearn.load_iris"
    x, y, note = load_dataset(name, Path("datasets/real/a3_cache"))
    return np.asarray(x, float), np.asarray(y, int), note


def _split(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=.25, random_state=314)
    train, test = next(splitter.split(x, y))
    return _subsample(train, y, TRAIN_CAP, 314), _subsample(test, y, TEST_CAP, 315)


def _metrics(prediction: np.ndarray, y: np.ndarray) -> float:
    return float((prediction == y).mean())


def evaluate() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for dataset in DATASETS:
        x, y, source = _load(dataset)
        train_ids, test_ids = _split(x, y)
        x_train, x_test = _transform_fit(x[train_ids], x[test_ids])
        y_train, y_test = y[train_ids], y[test_ids]
        for perturbation, strength in SCENARIOS:
            for perturbation_seed in SEEDS:
                if perturbation == "label_flip":
                    variant_ids, x_variant, y_variant, x_test_variant = train_ids, x_train, _flip_labels(y_train, strength, perturbation_seed), x_test
                else:
                    variant_ids = _delete_indices(train_ids, y_train, strength, perturbation_seed)
                    keep = np.isin(train_ids, variant_ids)
                    x_variant, x_test_variant = _transform_fit(x[variant_ids], x[test_ids])
                    y_variant = y_train[keep]
                for generator in GENERATORS:
                    original = _fit_structure(generator, x_train, y_train, train_ids, seed=1)
                    perturbed = _fit_structure(generator, x_variant, y_variant, variant_ids, seed=1)
                    original_prediction = _nearest_center_predict(original, x_test)
                    perturbed_prediction = _nearest_center_predict(perturbed, x_test_variant)
                    rows.append({
                        "dataset": dataset, "source": source, "generator": generator,
                        "implementation": "repository_cleanroom" if generator != "gbc_confidence_bound_control" else "repository_internal_control",
                        "decision_rule": "nearest_center", "perturbation_type": perturbation,
                        "perturbation_strength": strength, "seed": perturbation_seed,
                        **_partition_metrics(original, perturbed),
                        "prediction_agreement": float((original_prediction == perturbed_prediction).mean()),
                        "accuracy_original": _metrics(original_prediction, y_test),
                        "accuracy_perturbed": _metrics(perturbed_prediction, y_test),
                        "accuracy_change": abs(_metrics(original_prediction, y_test) - _metrics(perturbed_prediction, y_test)),
                        "ball_count_original": len(original.sizes), "ball_count_perturbed": len(perturbed.sizes),
                    })
    return pd.DataFrame(rows)
