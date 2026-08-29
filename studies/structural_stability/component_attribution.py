"""Hold granular structures fixed while changing only prediction decisions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

from studies.structural_stability.cheap_test import (
    GENERATORS,
    _delete_indices,
    _fit_structure,
    _flip_labels,
    _load_dataset,
    _partition_metrics,
    _split_dataset,
    _transform_fit,
)


SCENARIOS = (
    ("internet_ads", "label_flip", .05),
    ("htru2", "label_flip", .10),
    ("dry_bean", "label_flip", .01),
    ("micromass_pure_species", "sample_deletion", .01),
)
SEEDS = (1, 7, 21, 42, 2026)
DECISIONS = ("nearest_center", "radius_aware_distance", "three_center_inverse_distance_vote", "native_radius_aware")


def _predict(structure, x: np.ndarray, decision: str) -> np.ndarray:
    distances = np.linalg.norm(x[:, None, :] - structure.centers[None, :, :], axis=2)
    if decision == "nearest_center":
        indices = np.argmin(distances, axis=1)
        return structure.labels[indices]
    if decision in {"radius_aware_distance", "native_radius_aware"}:
        indices = np.argmin(distances - structure.radii[None, :], axis=1)
        return structure.labels[indices]
    if decision == "three_center_inverse_distance_vote":
        nearest = np.argsort(distances, axis=1)[:, : min(3, distances.shape[1])]
        labels = np.unique(structure.labels)
        output = []
        for row, centers in enumerate(nearest):
            weights = 1 / np.maximum(distances[row, centers], 1e-12)
            scores = np.asarray([weights[structure.labels[centers] == label].sum() for label in labels])
            output.append(labels[int(np.argmax(scores))])
        return np.asarray(output)
    raise ValueError(decision)


def _metrics(prediction: np.ndarray, y: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "macro_f1": float(f1_score(y, prediction, average="macro", zero_division=0)),
    }


def _structures(dataset: str, perturbation: str, strength: float, seed: int, root: Path):
    x, y, source = _load_dataset(dataset, root)
    train_ids, test_ids = _split_dataset(x, y)
    x_train_raw, x_test_raw, y_train, y_test = x[train_ids], x[test_ids], y[train_ids], y[test_ids]
    x_train, x_test = _transform_fit(x_train_raw, x_test_raw)
    if perturbation == "label_flip":
        return source, train_ids, x_train, y_train, x_test, y_test, train_ids, x_train, _flip_labels(y_train, strength, seed), x_test
    if perturbation == "sample_deletion":
        keep_ids = _delete_indices(train_ids, y_train, strength, seed)
        keep_mask = np.isin(train_ids, keep_ids)
        x_variant, x_test_variant = _transform_fit(x[keep_ids], x_test_raw)
        return source, train_ids, x_train, y_train, x_test, y_test, keep_ids, x_variant, y_train[keep_mask], x_test_variant
    raise ValueError(perturbation)


def evaluate() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    root = Path("datasets/real/a3_approved")
    for dataset, perturbation, strength in SCENARIOS:
        for seed in SEEDS:
            source, original_ids, x_original, y_original, x_test_original, y_test, perturbed_ids, x_perturbed, y_perturbed, x_test_perturbed = _structures(dataset, perturbation, strength, seed, root)
            for generator in GENERATORS:
                original = _fit_structure(generator, x_original, y_original, original_ids, seed=1)
                perturbed = _fit_structure(generator, x_perturbed, y_perturbed, perturbed_ids, seed=1)
                partition = _partition_metrics(original, perturbed)
                nearest_original = _metrics(_predict(original, x_test_original, "nearest_center"), y_test)
                nearest_perturbed = _metrics(_predict(perturbed, x_test_perturbed, "nearest_center"), y_test)
                for decision in DECISIONS:
                    prediction_original = _predict(original, x_test_original, decision)
                    prediction_perturbed = _predict(perturbed, x_test_perturbed, decision)
                    left = _metrics(prediction_original, y_test)
                    right = _metrics(prediction_perturbed, y_test)
                    rows.append({
                        "dataset": dataset, "source": source, "generator": generator,
                        "implementation": "repository_cleanroom" if generator != "gbc_confidence_bound_control" else "repository_internal_control",
                        "perturbation_type": perturbation, "perturbation_strength": strength, "seed": seed,
                        "decision_rule": decision, **partition,
                        "prediction_agreement": float((prediction_original == prediction_perturbed).mean()),
                        "accuracy_original": left["accuracy"], "accuracy_perturbed": right["accuracy"],
                        "balanced_accuracy_original": left["balanced_accuracy"], "balanced_accuracy_perturbed": right["balanced_accuracy"],
                        "macro_f1_original": left["macro_f1"], "macro_f1_perturbed": right["macro_f1"],
                        "decision_accuracy_gain_original_vs_nearest": left["accuracy"] - nearest_original["accuracy"],
                        "decision_accuracy_gain_perturbed_vs_nearest": right["accuracy"] - nearest_perturbed["accuracy"],
                        "native_decision_gain_original": left["accuracy"] - nearest_original["accuracy"] if decision == "native_radius_aware" else float("nan"),
                        "native_decision_gain_perturbed": right["accuracy"] - nearest_perturbed["accuracy"] if decision == "native_radius_aware" else float("nan"),
                    })
    return pd.DataFrame(rows)
