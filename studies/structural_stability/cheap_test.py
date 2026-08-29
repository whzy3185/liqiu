"""Frozen-v1 structural/predictive stability audit for existing GBC paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    balanced_accuracy_score,
    mutual_info_score,
    normalized_mutual_info_score,
    f1_score,
)
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import LabelEncoder, StandardScaler

from baselines.gbc import ConfidenceBoundGranularBallClassifier, GranularBallClassifier
from studies.dataset_mining.approved_loaders import load_approved
from studies.privacy_refinement.a3 import synthetic_regime
from studies.risk_granularity.tree import GranulationTree, Node


DATASETS = (
    "breast_cancer", "wine", "digits", "dry_bean", "htru2", "internet_ads",
    "micromass_pure_species", "a3_geometry_label_conflict_synthetic",
)
GENERATORS = (
    "tree_kmeans_binary", "tree_class_means_binary", "gbc_multiclass_cleanroom",
    "gbc_confidence_bound_control",
)
SEEDS = (1, 7, 21, 42, 2026)
TRAIN_CAP = 500
TEST_CAP = 500
PURITY = .85


@dataclass(frozen=True)
class Structure:
    assignment: dict[int, int]
    centers: np.ndarray
    labels: np.ndarray
    sizes: np.ndarray
    radii: np.ndarray
    purities: np.ndarray
    depths: np.ndarray


def _load_dataset(name: str, root: Path) -> tuple[np.ndarray, np.ndarray, str]:
    if name == "breast_cancer":
        data = load_breast_cancer()
        return np.asarray(data.data, float), np.asarray(data.target, int), "sklearn.load_breast_cancer"
    if name == "wine":
        data = load_wine()
        return np.asarray(data.data, float), np.asarray(data.target, int), "sklearn.load_wine"
    if name == "digits":
        data = load_digits()
        return np.asarray(data.data, float), np.asarray(data.target, int), "sklearn.load_digits"
    if name == "a3_geometry_label_conflict_synthetic":
        x, y = synthetic_regime(
            n=1_100, dimension=40, separation=1.0, density_ratio=2.5,
            minority_fraction=.25, modes=3, redundant_fraction=.10,
            label_noise=.08, seed=2026,
        )
        return x, y, "A3 synthetic controlled geometry-label-conflict stress family; not privacy evidence"
    source_id = {
        "dry_bean": "uci-602", "htru2": "uci-372", "internet_ads": "uci-51",
        "micromass_pure_species": "uci-253",
    }[name]
    x, y, note = load_approved(root, source_id)
    return np.asarray(x, float), LabelEncoder().fit_transform(y), note


def _subsample(indices: np.ndarray, y: np.ndarray, cap: int, seed: int) -> np.ndarray:
    if len(indices) <= cap:
        return indices
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=cap, random_state=seed)
    chosen, _ = next(splitter.split(np.zeros((len(indices), 1)), y[indices]))
    return indices[chosen]


def _split_dataset(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=.25, random_state=2026)
    train, test = next(splitter.split(x, y))
    return _subsample(train, y, TRAIN_CAP, 2026), _subsample(test, y, TEST_CAP, 2027)


def _transform_fit(x_train: np.ndarray, x_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median").fit(x_train)
    scaler = StandardScaler().fit(imputer.transform(x_train))
    return scaler.transform(imputer.transform(x_train)), scaler.transform(imputer.transform(x_test))


def _tree_depths(root: Node) -> dict[int, int]:
    result: dict[int, int] = {}
    def visit(node: Node, depth: int) -> None:
        result[id(node)] = depth
        for child in node.children:
            visit(child, depth + 1)
    visit(root, 0)
    return result


def _fit_structure(generator: str, x: np.ndarray, y: np.ndarray, original_ids: np.ndarray, seed: int) -> Structure:
    if generator.startswith("tree_"):
        method = "kmeans" if generator == "tree_kmeans_binary" else "class_means"
        tree = GranulationTree(random_state=seed, split_method=method).fit(x, y)
        leaves = tree.cut(PURITY)
        depths = _tree_depths(tree.root)
        members = [leaf.indices for leaf in leaves]
        centers = np.vstack([leaf.center for leaf in leaves])
        labels = np.asarray([leaf.label for leaf in leaves])
        radii = np.asarray([leaf.radius for leaf in leaves])
        purities = np.asarray([leaf.purity for leaf in leaves])
        leaf_depths = np.asarray([depths[id(leaf)] for leaf in leaves])
    else:
        model = GranularBallClassifier(purity=PURITY, random_state=seed) if generator == "gbc_multiclass_cleanroom" else ConfidenceBoundGranularBallClassifier(purity=PURITY, random_state=seed)
        model.fit(x, y)
        members = [ball.members for ball in model.balls_]
        centers = np.vstack([ball.center for ball in model.balls_])
        labels = np.asarray([ball.label for ball in model.balls_])
        radii = np.asarray([ball.radius for ball in model.balls_])
        purities = np.asarray([ball.purity for ball in model.balls_])
        leaf_depths = np.full(len(members), np.nan)
    assignment: dict[int, int] = {}
    for ball_id, member in enumerate(members):
        for local_id in member:
            assignment[int(original_ids[int(local_id)])] = ball_id
    if len(assignment) != len(original_ids):
        raise RuntimeError(f"{generator} did not assign every training sample")
    return Structure(assignment, centers, labels, np.asarray([len(member) for member in members]), radii, purities, leaf_depths)


def _nearest_center_predict(structure: Structure, x: np.ndarray) -> np.ndarray:
    nearest = np.argmin(np.linalg.norm(x[:, None, :] - structure.centers[None, :, :], axis=2), axis=1)
    return structure.labels[nearest]


def _vi(left: np.ndarray, right: np.ndarray) -> float:
    # Natural-log variation of information; zero means identical partitions.
    def entropy(values: np.ndarray) -> float:
        _, counts = np.unique(values, return_counts=True)
        probabilities = counts / counts.sum()
        return float(-(probabilities * np.log(probabilities)).sum())
    return entropy(left) + entropy(right) - 2 * float(mutual_info_score(left, right))


def _distribution_change(left: np.ndarray, right: np.ndarray) -> float:
    return float(wasserstein_distance(left, right))


def _partition_metrics(original: Structure, perturbed: Structure) -> dict[str, float | int]:
    common = np.asarray(sorted(set(original.assignment).intersection(perturbed.assignment)), dtype=int)
    if not len(common):
        raise RuntimeError("no common training samples")
    left = np.asarray([original.assignment[int(index)] for index in common])
    right = np.asarray([perturbed.assignment[int(index)] for index in common])
    return {
        "n_common_samples": len(common),
        "ari": float(adjusted_rand_score(left, right)),
        "nmi": float(normalized_mutual_info_score(left, right)),
        "vi": _vi(left, right),
    }


def _descriptive_change(original: Structure, perturbed: Structure) -> dict[str, float]:
    return {
        "ball_count_original": len(original.sizes),
        "ball_count_perturbed": len(perturbed.sizes),
        "ball_count_ratio": float(len(perturbed.sizes) / len(original.sizes)),
        "absolute_ball_count_change": float(abs(len(perturbed.sizes) - len(original.sizes))),
        "median_ball_size_original": float(np.median(original.sizes)),
        "median_ball_size_perturbed": float(np.median(perturbed.sizes)),
        "singleton_ratio_original": float((original.sizes == 1).mean()),
        "singleton_ratio_perturbed": float((perturbed.sizes == 1).mean()),
        "radius_distribution_change": _distribution_change(original.radii, perturbed.radii),
        "purity_distribution_change": _distribution_change(original.purities, perturbed.purities),
        "mean_refinement_depth_original": float(np.nanmean(original.depths)) if np.isfinite(original.depths).any() else float("nan"),
        "mean_refinement_depth_perturbed": float(np.nanmean(perturbed.depths)) if np.isfinite(perturbed.depths).any() else float("nan"),
    }


def _predictions(structure: Structure, x_test: np.ndarray, y_test: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    prediction = _nearest_center_predict(structure, x_test)
    return prediction, {
        "accuracy": float(accuracy_score(y_test, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, prediction)),
        "macro_f1": float(f1_score(y_test, prediction, average="macro", zero_division=0)),
    }


def _delete_indices(ids: np.ndarray, y: np.ndarray, fraction: float, seed: int) -> np.ndarray:
    keep_size = max(len(np.unique(y)) * 2, int(round(len(ids) * (1 - fraction))))
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=keep_size, random_state=seed)
    keep, _ = next(splitter.split(np.zeros((len(ids), 1)), y))
    return ids[keep]


def _flip_labels(y: np.ndarray, fraction: float, seed: int) -> np.ndarray:
    result = y.copy()
    rng = np.random.default_rng(seed)
    positions = rng.choice(len(y), size=max(1, int(round(len(y) * fraction))), replace=False)
    labels = np.unique(y)
    for position in positions:
        result[position] = rng.choice(labels[labels != result[position]])
    return result


def _row(
    dataset: str, source: str, generator: str, perturbation_type: str,
    strength: float | str, seed: int, original: Structure, perturbed: Structure,
    original_prediction: np.ndarray, perturbed_prediction: np.ndarray,
    original_metrics: dict[str, float], perturbed_metrics: dict[str, float], runtime: float,
) -> dict[str, object]:
    return {
        "dataset": dataset, "source": source, "generator": generator,
        "implementation": "repository_cleanroom" if generator != "gbc_confidence_bound_control" else "repository_internal_control",
        "decision_rule": "nearest_center", "perturbation_type": perturbation_type,
        "perturbation_strength": strength, "seed": seed,
        **_partition_metrics(original, perturbed), **_descriptive_change(original, perturbed),
        "prediction_agreement": float((original_prediction == perturbed_prediction).mean()),
        "accuracy_original": original_metrics["accuracy"], "accuracy_perturbed": perturbed_metrics["accuracy"],
        "accuracy_change": abs(original_metrics["accuracy"] - perturbed_metrics["accuracy"]),
        "balanced_accuracy_original": original_metrics["balanced_accuracy"], "balanced_accuracy_perturbed": perturbed_metrics["balanced_accuracy"],
        "macro_f1_original": original_metrics["macro_f1"], "macro_f1_perturbed": perturbed_metrics["macro_f1"],
        "runtime_seconds": runtime,
    }


def evaluate_dataset(dataset: str, root: Path, *, smoke: bool = False) -> list[dict[str, object]]:
    x, y, source = _load_dataset(dataset, root)
    train_ids, test_ids = _split_dataset(x, y)
    x_train_raw, x_test_raw = x[train_ids], x[test_ids]
    y_train, y_test = y[train_ids], y[test_ids]
    x_train_base, x_test_base = _transform_fit(x_train_raw, x_test_raw)
    seeds = (1, 7) if smoke else SEEDS
    sample_levels = (.01,) if smoke else (.01, .05)
    label_levels = (.01,) if smoke else (.01, .05, .10)
    feature_levels = (.01,) if smoke else (.01, .05)
    rows: list[dict[str, object]] = []
    for generator in GENERATORS:
        base_start = time.perf_counter()
        original = _fit_structure(generator, x_train_base, y_train, train_ids, seed=1)
        original_prediction, original_metrics = _predictions(original, x_test_base, y_test)
        base_runtime = time.perf_counter() - base_start
        rows.append(_row(dataset, source, generator, "seed", "baseline", 1, original, original, original_prediction, original_prediction, original_metrics, original_metrics, base_runtime))
        for seed in seeds:
            if seed == 1:
                continue
            started = time.perf_counter()
            perturbed = _fit_structure(generator, x_train_base, y_train, train_ids, seed=seed)
            prediction, metrics = _predictions(perturbed, x_test_base, y_test)
            rows.append(_row(dataset, source, generator, "seed", "fixed_data", seed, original, perturbed, original_prediction, prediction, original_metrics, metrics, time.perf_counter() - started))
        for fraction in sample_levels:
            for seed in seeds:
                keep_ids = _delete_indices(train_ids, y_train, fraction, seed)
                keep_positions = np.isin(train_ids, keep_ids)
                x_variant, x_test_variant = _transform_fit(x[keep_ids], x_test_raw)
                started = time.perf_counter()
                perturbed = _fit_structure(generator, x_variant, y_train[keep_positions], keep_ids, seed=1)
                prediction, metrics = _predictions(perturbed, x_test_variant, y_test)
                rows.append(_row(dataset, source, generator, "sample_deletion", fraction, seed, original, perturbed, original_prediction, prediction, original_metrics, metrics, time.perf_counter() - started))
        for fraction in label_levels:
            for seed in seeds:
                started = time.perf_counter()
                perturbed = _fit_structure(generator, x_train_base, _flip_labels(y_train, fraction, seed), train_ids, seed=1)
                prediction, metrics = _predictions(perturbed, x_test_base, y_test)
                rows.append(_row(dataset, source, generator, "label_flip", fraction, seed, original, perturbed, original_prediction, prediction, original_metrics, metrics, time.perf_counter() - started))
        for sigma in feature_levels:
            for seed in seeds:
                rng = np.random.default_rng(seed)
                started = time.perf_counter()
                perturbed = _fit_structure(generator, x_train_base + rng.normal(0, sigma, size=x_train_base.shape), y_train, train_ids, seed=1)
                prediction, metrics = _predictions(perturbed, x_test_base, y_test)
                rows.append(_row(dataset, source, generator, "feature_gaussian", sigma, seed, original, perturbed, original_prediction, prediction, original_metrics, metrics, time.perf_counter() - started))
    return rows


def evaluate(datasets: tuple[str, ...] = DATASETS, *, smoke: bool = False) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    root = Path("datasets/real/a3_approved")
    for dataset in datasets:
        rows.extend(evaluate_dataset(dataset, root, smoke=smoke))
    return pd.DataFrame(rows)
