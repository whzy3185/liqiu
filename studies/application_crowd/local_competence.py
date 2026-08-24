"""Local annotator competence and capacity-limited label allocation."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import load_breast_cancer, load_digits, make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from studies.application_cleaning.cell_context import build_context_tree


DATASETS = ("moons", "breast_cancer", "digits")
REGIMES = ("axis", "voronoi", "nonlinear", "global_control")
METHODS = (
    "gb_surface_multiscale",
    "gb_center_multiscale",
    "gb_surface_terminal",
    "gb_center_terminal",
    "kmeans_local",
    "knn_local",
    "tree_local",
    "dawid_skene",
    "majority_vote",
    "oracle_local",
)
WORKER_TYPES = (
    "global_good",
    "global_good",
    "global_bad",
    "global_bad",
    "region_specialist",
    "region_specialist",
    "region_specialist",
    "region_specialist",
    "class_specialist",
    "class_specialist",
    "class_specialist",
    "boundary_poor",
    "boundary_poor",
    "boundary_poor",
    "local_adversarial",
    "local_adversarial",
)


def _load(dataset: str, seed: int, max_samples: int | None = None):
    if dataset == "moons":
        features, labels = make_moons(n_samples=2000, noise=0.22, random_state=seed)
    elif dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    else:
        raise ValueError(dataset)
    if max_samples is not None and len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    return np.asarray(features, float), np.asarray(labels, int)


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=1, keepdims=True)


def _majority(annotation: np.ndarray, classes: int) -> np.ndarray:
    counts = np.ones((len(annotation), classes), dtype=float)
    for label in range(classes):
        counts[:, label] += np.sum(annotation == label, axis=1)
    return counts / counts.sum(axis=1, keepdims=True)


def fit_dawid_skene(annotation: np.ndarray, classes: int, iterations: int = 30):
    posterior = _majority(annotation, classes)
    confusion = np.zeros((annotation.shape[1], classes, classes), dtype=float)
    priors = posterior.mean(axis=0)
    for _ in range(iterations):
        for worker in range(annotation.shape[1]):
            confusion[worker] = 1.0
            confusion[worker, np.arange(classes), np.arange(classes)] += 1.0
            observed = np.flatnonzero(annotation[:, worker] >= 0)
            for item in observed:
                confusion[worker, :, annotation[item, worker]] += posterior[item]
            confusion[worker] /= confusion[worker].sum(axis=1, keepdims=True)
        priors = np.maximum(posterior.mean(axis=0), 1e-9)
        logits = np.tile(np.log(priors), (len(annotation), 1))
        for worker in range(annotation.shape[1]):
            observed = np.flatnonzero(annotation[:, worker] >= 0)
            if len(observed):
                logits[observed] += np.log(
                    np.maximum(confusion[worker, :, annotation[observed, worker]], 1e-12)
                )
        updated = _softmax(logits)
        if np.max(np.abs(updated - posterior)) < 1e-8:
            posterior = updated
            break
        posterior = updated
    return posterior, priors, confusion


def _ds_predict(annotation, priors, confusion):
    logits = np.tile(np.log(np.maximum(priors, 1e-12)), (len(annotation), 1))
    for worker in range(annotation.shape[1]):
        observed = np.flatnonzero(annotation[:, worker] >= 0)
        if len(observed):
            logits[observed] += np.log(
                np.maximum(confusion[worker, :, annotation[observed, worker]], 1e-12)
            )
    return _softmax(logits)


def _fit_region_map(kind, fit_x, query_x, seed):
    if kind in ("axis", "global_control"):
        first = fit_x[:, 0]
        second = fit_x[:, min(1, fit_x.shape[1] - 1)]
        thresholds = (np.median(first), np.median(second))
        fit = (first > thresholds[0]).astype(int) + 2 * (second > thresholds[1]).astype(int)
        query = (query_x[:, 0] > thresholds[0]).astype(int) + 2 * (
            query_x[:, min(1, query_x.shape[1] - 1)] > thresholds[1]
        ).astype(int)
        return fit, query
    if kind == "voronoi":
        model = KMeans(4, n_init=10, random_state=seed).fit(fit_x)
        return model.labels_, model.predict(query_x)
    if kind == "nonlinear":
        rng = np.random.default_rng(seed)
        width = min(8, fit_x.shape[1])
        weights = rng.normal(size=(fit_x.shape[1], width))
        offsets = rng.uniform(-np.pi, np.pi, size=width)
        fit_map = np.sin(fit_x @ weights + offsets)
        query_map = np.sin(query_x @ weights + offsets)
        model = KMeans(4, n_init=10, random_state=seed + 1).fit(fit_map)
        return model.labels_, model.predict(query_map)
    raise ValueError(kind)


def _boundary_mask(fit_x, fit_y, query_x, query_y):
    classes = np.unique(fit_y)
    centers = np.vstack([fit_x[fit_y == label].mean(axis=0) for label in classes])

    def margin(features, labels):
        distances = np.linalg.norm(features[:, None, :] - centers[None, :, :], axis=2)
        own = distances[np.arange(len(features)), labels]
        distances[np.arange(len(features)), labels] = np.inf
        return distances.min(axis=1) - own

    fit_margin = margin(fit_x, fit_y)
    threshold = float(np.quantile(fit_margin, 0.25))
    return fit_margin <= threshold, margin(query_x, query_y) <= threshold


def _worker_probabilities(regime, fit_regions, query_regions, fit_boundary, query_boundary, fit_y, query_y):
    classes = len(np.unique(fit_y))
    random_floor = 1.0 / classes + 0.02
    fit = np.zeros((len(fit_y), len(WORKER_TYPES)))
    query = np.zeros((len(query_y), len(WORKER_TYPES)))
    for worker, worker_type in enumerate(WORKER_TYPES):
        if regime == "global_control":
            value = 0.90 if worker < len(WORKER_TYPES) // 2 else max(0.55, random_floor)
            fit[:, worker] = value
            query[:, worker] = value
            continue
        if worker_type == "global_good":
            fit[:, worker] = query[:, worker] = 0.90
        elif worker_type == "global_bad":
            fit[:, worker] = query[:, worker] = max(0.55, random_floor)
        elif worker_type == "region_specialist":
            region = worker % 4
            fraction = max(float(np.mean(fit_regions == region)), 0.05)
            outside = np.clip((0.70 - fraction * 0.95) / (1 - fraction), random_floor, 0.90)
            fit[:, worker] = np.where(fit_regions == region, 0.95, outside)
            query[:, worker] = np.where(query_regions == region, 0.95, outside)
        elif worker_type == "class_specialist":
            label = worker % classes
            fraction = max(float(np.mean(fit_y == label)), 0.05)
            outside = np.clip((0.70 - fraction * 0.95) / (1 - fraction), random_floor, 0.90)
            fit[:, worker] = np.where(fit_y == label, 0.95, outside)
            query[:, worker] = np.where(query_y == label, 0.95, outside)
        elif worker_type == "boundary_poor":
            fraction = max(float(np.mean(fit_boundary)), 0.05)
            poor = 1.0 / classes
            outside = np.clip((0.70 - fraction * poor) / (1 - fraction), random_floor, 0.98)
            fit[:, worker] = np.where(fit_boundary, poor, outside)
            query[:, worker] = np.where(query_boundary, poor, outside)
        elif worker_type == "local_adversarial":
            region = worker % 4
            fraction = max(float(np.mean(fit_regions == region)), 0.05)
            outside = np.clip((0.70 - fraction * 0.05) / (1 - fraction), random_floor, 0.98)
            fit[:, worker] = np.where(fit_regions == region, 0.05, outside)
            query[:, worker] = np.where(query_regions == region, 0.05, outside)
        else:
            raise ValueError(worker_type)
    return fit, query


def _realize_labels(labels, probabilities, seed):
    rng = np.random.default_rng(seed)
    classes = len(np.unique(labels))
    annotation = np.empty_like(probabilities, dtype=int)
    for item, truth in enumerate(labels):
        for worker in range(probabilities.shape[1]):
            if rng.random() < probabilities[item, worker]:
                annotation[item, worker] = truth
            elif WORKER_TYPES[worker] == "local_adversarial" and probabilities[item, worker] < 0.10:
                annotation[item, worker] = (truth + 1) % classes
            else:
                wrong = rng.integers(classes - 1)
                annotation[item, worker] = wrong + (wrong >= truth)
    return annotation


def _observation_mask(items, workers, labels_per_item, seed):
    rng = np.random.default_rng(seed)
    mask = np.zeros((items, workers), dtype=bool)
    for item in range(items):
        offset = (item * labels_per_item + rng.integers(workers)) % workers
        chosen = (offset + rng.permutation(workers)[:labels_per_item]) % workers
        mask[item, chosen] = True
    return mask


def _global_reliability(annotation, posterior):
    workers = annotation.shape[1]
    values = np.empty(workers)
    soft = np.full_like(annotation, np.nan, dtype=float)
    for worker in range(workers):
        observed = np.flatnonzero(annotation[:, worker] >= 0)
        correctness = posterior[observed, annotation[observed, worker]]
        soft[observed, worker] = correctness
        values[worker] = (correctness.sum() + 2.0) / (len(correctness) + 4.0)
    return values, soft


def _node_reliability(tree, soft, global_q, kappa=10.0):
    stats = np.empty((len(tree.nodes), soft.shape[1]))
    for node_id, node in enumerate(tree.nodes):
        parent = global_q if node.parent is None else stats[node.parent]
        for worker in range(soft.shape[1]):
            values = soft[node.indices, worker]
            values = values[np.isfinite(values)]
            stats[node_id, worker] = (values.sum() + kappa * parent[worker]) / (
                len(values) + kappa
            )
    return stats


def _route_nodes(tree, cut, query, surface):
    centers = np.vstack([tree.nodes[node].center for node in cut])
    distances = np.linalg.norm(query[:, None, :] - centers[None, :, :], axis=2)
    if surface:
        radii = np.asarray([tree.nodes[node].radius for node in cut])
        distances = (distances - radii[None, :]) / radii[None, :]
    return np.asarray(cut)[np.argmin(distances, axis=1)]


def _gb_reliability(tree, stats, query, surface, multiscale):
    cuts = tree.cuts()
    if not multiscale:
        cuts = [cuts[-1]]
    levels = []
    for cut in cuts:
        assigned = _route_nodes(tree, cut, query, surface)
        levels.append(stats[assigned])
    return np.mean(levels, axis=0)


def _kmeans_reliability(fit_x, query_x, soft, global_q, count, seed, kappa=10.0):
    model = KMeans(count, n_init=10, random_state=seed).fit(fit_x)
    query_labels = model.predict(query_x)
    output = np.empty((len(query_x), soft.shape[1]))
    stats = np.empty((count, soft.shape[1]))
    for cluster in range(count):
        members = model.labels_ == cluster
        for worker in range(soft.shape[1]):
            values = soft[members, worker]
            values = values[np.isfinite(values)]
            stats[cluster, worker] = (values.sum() + kappa * global_q[worker]) / (
                len(values) + kappa
            )
    output[:] = stats[query_labels]
    return output


def _knn_reliability(fit_x, query_x, soft, global_q, neighbors, kappa=10.0):
    neighbor_ids = NearestNeighbors(n_neighbors=min(neighbors, len(fit_x))).fit(fit_x).kneighbors(
        query_x, return_distance=False
    )
    output = np.empty((len(query_x), soft.shape[1]))
    for item, local in enumerate(neighbor_ids):
        for worker in range(soft.shape[1]):
            values = soft[local, worker]
            values = values[np.isfinite(values)]
            output[item, worker] = (values.sum() + kappa * global_q[worker]) / (
                len(values) + kappa
            )
    return output


def _tree_reliability(fit_x, query_x, soft, global_q, leaves, min_leaf, seed):
    output = np.empty((len(query_x), soft.shape[1]))
    for worker in range(soft.shape[1]):
        observed = np.flatnonzero(np.isfinite(soft[:, worker]))
        if len(observed) < 2 * min_leaf:
            output[:, worker] = global_q[worker]
            continue
        model = DecisionTreeRegressor(
            max_leaf_nodes=max(2, leaves),
            min_samples_leaf=min_leaf,
            random_state=seed + worker,
        ).fit(fit_x[observed], soft[observed, worker])
        output[:, worker] = np.clip(model.predict(query_x), 0.01, 0.99)
    return output


def _symmetric_aggregate(annotation, reliability, priors, classes):
    logits = np.tile(np.log(np.maximum(priors, 1e-12)), (len(annotation), 1))
    for item in range(len(annotation)):
        for worker in np.flatnonzero(annotation[item] >= 0):
            observed = annotation[item, worker]
            q = float(np.clip(reliability[item, worker], 0.01, 0.99))
            likelihood = np.full(classes, max((1 - q) / max(classes - 1, 1), 1e-12))
            likelihood[observed] = max(q, 1e-12)
            logits[item] += np.log(likelihood)
    return _softmax(logits)


def _ece(labels, probabilities, bins=10):
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    edges = np.linspace(0, 1, bins + 1)
    value = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        selected = (confidence >= low) & (confidence < (high if high < 1 else high + 1e-12))
        if selected.any():
            value += selected.mean() * abs((prediction[selected] == labels[selected]).mean() - confidence[selected].mean())
    return float(value)


def _allocation_curve(annotation, initial_mask, probe_mask, labels, reliability, priors, classes, seed, ds_confusion=None):
    revealed = initial_mask.copy()
    worker_counts = np.zeros(annotation.shape[1], dtype=int)
    budgets = (0, int(np.ceil(0.25 * len(labels))), int(np.ceil(0.50 * len(labels))), len(labels))
    curve = []
    rng = np.random.default_rng(seed)
    for target_budget in budgets:
        current = int(worker_counts.sum())
        if current < target_budget:
            if ds_confusion is None:
                posterior = _symmetric_aggregate(
                    np.where(revealed, annotation, -1), reliability, priors, classes
                )
            else:
                posterior = _ds_predict(np.where(revealed, annotation, -1), priors, ds_confusion)
            entropy = -np.sum(posterior * np.log(np.maximum(posterior, 1e-12)), axis=1)
            candidates = []
            for item in range(len(labels)):
                for worker in range(annotation.shape[1]):
                    if revealed[item, worker] or probe_mask[item, worker]:
                        continue
                    information = entropy[item] * (reliability[item, worker] - 1 / classes) ** 2
                    candidates.append((information + 1e-12 * rng.random(), item, worker))
            capacity = int(np.ceil(target_budget / annotation.shape[1])) + 1
            for _, item, worker in sorted(candidates, reverse=True):
                if worker_counts[worker] >= capacity:
                    continue
                revealed[item, worker] = True
                worker_counts[worker] += 1
                if worker_counts.sum() >= target_budget:
                    break
        observed = np.where(revealed, annotation, -1)
        if ds_confusion is None:
            posterior = _symmetric_aggregate(observed, reliability, priors, classes)
        else:
            posterior = _ds_predict(observed, priors, ds_confusion)
        curve.append(
            {
                "budget": int(worker_counts.sum()),
                "cost_fraction": float(worker_counts.sum() / max(len(labels), 1)),
                "accuracy": float(accuracy_score(labels, posterior.argmax(axis=1))),
                "nll": float(log_loss(labels, posterior, labels=np.arange(classes))),
            }
        )
    x = np.asarray([row["cost_fraction"] for row in curve])
    y = np.asarray([row["accuracy"] for row in curve])
    auc = float(np.trapezoid(y, x) / max(x[-1] - x[0], 1e-12))
    return curve, auc, revealed


def _method_metrics(name, probabilities, reliability, pool_annotation, pool_labels, probe_mask, curve, allocation_auc, runtime, regions, outer_x, outer_y, pool_x, final_revealed, priors, classes, ds_confusion=None):
    probe_items, probe_workers = np.nonzero(probe_mask)
    actual_correct = (
        pool_annotation[probe_items, probe_workers] == pool_labels[probe_items]
    ).astype(int)
    predicted_correct = reliability[probe_items, probe_workers]
    prediction = probabilities.argmax(axis=1)
    region_scores = []
    for region in np.unique(regions):
        selected = regions == region
        region_scores.append(float(accuracy_score(pool_labels[selected], prediction[selected])))
    downstream = LogisticRegression(max_iter=2000, random_state=17).fit(pool_x, prediction)
    downstream_accuracy = float(accuracy_score(outer_y, downstream.predict(outer_x)))
    return {
        "method": name,
        "aggregation_accuracy": float(accuracy_score(pool_labels, prediction)),
        "macro_f1": float(f1_score(pool_labels, prediction, average="macro", zero_division=0)),
        "nll": float(log_loss(pool_labels, probabilities, labels=np.arange(classes))),
        "ece": _ece(pool_labels, probabilities),
        "worst_region_accuracy": min(region_scores),
        "competence_auprc": float(average_precision_score(actual_correct, predicted_correct)),
        "competence_brier": float(brier_score_loss(actual_correct, predicted_correct)),
        "allocation_curve": curve,
        "allocation_accuracy_auc": allocation_auc,
        "downstream_accuracy": downstream_accuracy,
        "runtime_seconds": runtime,
    }


def evaluate_local_competence(dataset: str, regime: str, seed: int, max_samples: int | None = None):
    features, labels = _load(dataset, seed, max_samples=max_samples)
    outer_train, outer_test = train_test_split(
        np.arange(len(labels)), test_size=0.25, stratify=labels, random_state=seed
    )
    competence_ids, pool_ids = train_test_split(
        outer_train,
        test_size=1 / 3,
        stratify=labels[outer_train],
        random_state=seed + 1,
    )
    scaler = StandardScaler().fit(features[competence_ids])
    competence_x = scaler.transform(features[competence_ids])
    pool_x = scaler.transform(features[pool_ids])
    outer_x = scaler.transform(features[outer_test])
    competence_y, pool_y, outer_y = labels[competence_ids], labels[pool_ids], labels[outer_test]
    classes = len(np.unique(labels))
    fit_regions, pool_regions = _fit_region_map(regime, competence_x, pool_x, seed + 10)
    fit_boundary, pool_boundary = _boundary_mask(
        competence_x, competence_y, pool_x, pool_y
    )
    fit_prob, pool_prob = _worker_probabilities(
        regime, fit_regions, pool_regions, fit_boundary, pool_boundary, competence_y, pool_y
    )
    fit_latent = _realize_labels(competence_y, fit_prob, seed + 20)
    pool_latent = _realize_labels(pool_y, pool_prob, seed + 30)
    fit_mask = _observation_mask(len(competence_y), len(WORKER_TYPES), 5, seed + 40)
    pool_mask = _observation_mask(len(pool_y), len(WORKER_TYPES), 2, seed + 50)
    fit_annotation = np.where(fit_mask, fit_latent, -1)
    pool_initial = np.where(pool_mask, pool_latent, -1)
    probe_mask = np.zeros_like(pool_mask)
    for item in range(len(pool_y)):
        available = np.flatnonzero(~pool_mask[item])
        probe_mask[item, available[(item + seed) % len(available)]] = True

    ds_train, priors, confusion = fit_dawid_skene(fit_annotation, classes)
    global_q, soft_correct = _global_reliability(fit_annotation, ds_train)
    min_leaf = max(10, int(np.ceil(0.05 * len(competence_x))))
    budget = min(16, max(4, len(competence_x) // 40))
    tree = build_context_tree(competence_x, budget, seed + 60, min_leaf)
    stats = _node_reliability(tree, soft_correct, global_q)
    leaf_count = len(tree.leaves)
    median_leaf = int(np.median([len(tree.nodes[node].indices) for node in tree.leaves]))

    start = time.perf_counter()
    reliability = {
        "gb_surface_multiscale": _gb_reliability(tree, stats, pool_x, True, True),
        "gb_center_multiscale": _gb_reliability(tree, stats, pool_x, False, True),
        "gb_surface_terminal": _gb_reliability(tree, stats, pool_x, True, False),
        "gb_center_terminal": _gb_reliability(tree, stats, pool_x, False, False),
        "kmeans_local": _kmeans_reliability(
            competence_x, pool_x, soft_correct, global_q, leaf_count, seed + 70
        ),
        "knn_local": _knn_reliability(
            competence_x, pool_x, soft_correct, global_q, max(10, min(50, median_leaf))
        ),
        "tree_local": _tree_reliability(
            competence_x, pool_x, soft_correct, global_q, leaf_count, min_leaf, seed + 80
        ),
        "dawid_skene": np.tile(global_q, (len(pool_y), 1)),
        "majority_vote": np.full((len(pool_y), len(WORKER_TYPES)), 1.0 / classes),
        "oracle_local": pool_prob,
    }
    fit_seconds = time.perf_counter() - start
    rows = []
    for method in METHODS:
        start = time.perf_counter()
        q = reliability[method]
        if method == "majority_vote":
            probabilities = _majority(pool_initial, classes)
            method_priors = np.full(classes, 1 / classes)
            ds_confusion = None
        elif method == "dawid_skene":
            probabilities = _ds_predict(pool_initial, priors, confusion)
            method_priors = priors
            ds_confusion = confusion
        else:
            probabilities = _symmetric_aggregate(pool_initial, q, priors, classes)
            method_priors = priors
            ds_confusion = None
        curve, allocation_auc, final_revealed = _allocation_curve(
            pool_latent,
            pool_mask,
            probe_mask,
            pool_y,
            q,
            method_priors,
            classes,
            seed + 100 + METHODS.index(method),
            ds_confusion=ds_confusion,
        )
        runtime = fit_seconds + time.perf_counter() - start
        rows.append(
            _method_metrics(
                method,
                probabilities,
                q,
                pool_latent,
                pool_y,
                probe_mask,
                curve,
                allocation_auc,
                runtime,
                pool_regions,
                outer_x,
                outer_y,
                pool_x,
                final_revealed,
                method_priors,
                classes,
                ds_confusion=ds_confusion,
            )
        )
    return {
        "dataset": dataset,
        "regime": regime,
        "seed": seed,
        "items": {"competence": len(competence_y), "pool": len(pool_y), "outer_test": len(outer_y)},
        "classes": classes,
        "workers": len(WORKER_TYPES),
        "worker_types": list(WORKER_TYPES),
        "mean_worker_accuracy": float(fit_prob.mean()),
        "terminal_balls": leaf_count,
        "methods": rows,
    }
