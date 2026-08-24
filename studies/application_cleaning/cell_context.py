"""Cross-fitted contextual detection and repair of numeric cell errors."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import load_breast_cancer, load_diabetes, load_wine
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import KFold, train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.tree import DecisionTreeRegressor


DATASETS = ("breast_cancer", "wine", "diabetes")
METHODS = (
    "gb_surface_multiscale",
    "gb_center_multiscale",
    "kmeans_multiscale",
    "knn_context",
    "decision_tree",
    "global_robust",
)


def load_dataset(name: str):
    if name == "breast_cancer":
        bundle = load_breast_cancer()
        return bundle.data.astype(float), bundle.target, "classification"
    if name == "wine":
        bundle = load_wine()
        return bundle.data.astype(float), bundle.target, "classification"
    if name == "diabetes":
        bundle = load_diabetes()
        return bundle.data.astype(float), bundle.target, "regression"
    raise ValueError(name)


def _robust_scale(values: np.ndarray, floor: float) -> tuple[float, float]:
    median = float(np.median(values))
    mad = float(1.4826 * np.median(np.abs(values - median)))
    return median, max(mad, floor, 1e-6)


@dataclass
class ContextNode:
    indices: np.ndarray
    center: np.ndarray
    radius: float
    depth: int
    parent: int | None
    children: list[int] = field(default_factory=list)


@dataclass
class ContextTree:
    nodes: list[ContextNode]
    leaves: list[int]

    def cuts(self) -> list[list[int]]:
        output = []
        frontier = [0]
        output.append(frontier.copy())
        while any(self.nodes[node].children for node in frontier):
            expanded = []
            for node in frontier:
                expanded.extend(self.nodes[node].children or [node])
            frontier = expanded
            output.append(frontier.copy())
        return output


def _node(context: np.ndarray, indices: np.ndarray, depth: int, parent: int | None):
    local = context[indices]
    center = local.mean(axis=0)
    distances = np.linalg.norm(local - center, axis=1)
    radius = max(float(np.quantile(distances, 0.95)), 1e-6)
    return ContextNode(indices, center, radius, depth, parent)


def build_context_tree(
    context: np.ndarray,
    budget: int,
    seed: int,
    min_leaf: int,
    min_gain: float = 0.10,
) -> ContextTree:
    nodes = [_node(context, np.arange(len(context)), 0, None)]
    leaves = [0]
    blocked = set()
    split_round = 0
    while len(leaves) < budget:
        candidates = []
        for node_id in leaves:
            if node_id in blocked:
                continue
            node = nodes[node_id]
            if len(node.indices) < 2 * min_leaf:
                blocked.add(node_id)
                continue
            local = context[node.indices]
            center = local.mean(axis=0)
            dispersion = float(np.median(np.linalg.norm(local - center, axis=1)))
            candidates.append((dispersion * len(local), node_id, dispersion))
        if not candidates:
            break
        _, node_id, parent_dispersion = max(candidates)
        node = nodes[node_id]
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(
            context[node.indices]
        )
        child_indices = [node.indices[labels == value] for value in (0, 1)]
        if min(map(len, child_indices)) < min_leaf:
            blocked.add(node_id)
            continue
        child_dispersion = 0.0
        for indices in child_indices:
            local = context[indices]
            center = local.mean(axis=0)
            child_dispersion += len(indices) * float(
                np.median(np.linalg.norm(local - center, axis=1))
            )
        child_dispersion /= len(node.indices)
        gain = (parent_dispersion - child_dispersion) / max(parent_dispersion, 1e-6)
        if gain < min_gain:
            blocked.add(node_id)
            continue
        child_ids = []
        for indices in child_indices:
            child_ids.append(len(nodes))
            nodes.append(_node(context, indices, node.depth + 1, node_id))
        node.children = child_ids
        leaves[leaves.index(node_id) : leaves.index(node_id) + 1] = child_ids
        split_round += 1
    return ContextTree(nodes, leaves)


def _route(
    nodes: list[ContextNode], cut: list[int], query: np.ndarray, surface: bool
) -> np.ndarray:
    centers = np.vstack([nodes[node].center for node in cut])
    distances = np.linalg.norm(query[:, None, :] - centers[None, :, :], axis=2)
    if surface:
        radii = np.asarray([nodes[node].radius for node in cut])
        distances = (distances - radii[None, :]) / radii[None, :]
    return np.asarray(cut)[np.argmin(distances, axis=1)]


def _hierarchical_score(
    tree: ContextTree,
    target: np.ndarray,
    query_context: np.ndarray,
    query_target: np.ndarray,
    floor: float,
    surface: bool,
) -> tuple[np.ndarray, np.ndarray]:
    stats = {
        node_id: _robust_scale(target[node.indices], floor)
        for node_id, node in enumerate(tree.nodes)
    }
    scores = np.zeros(len(query_context))
    final_assignment = None
    for cut in tree.cuts():
        assignment = _route(tree.nodes, cut, query_context, surface)
        medians = np.asarray([stats[int(node)][0] for node in assignment])
        scales = np.asarray([stats[int(node)][1] for node in assignment])
        scores = np.maximum(scores, np.abs(query_target - medians) / scales)
        final_assignment = assignment
    proposals = np.asarray([stats[int(node)][0] for node in final_assignment])
    return scores, proposals


def _kmeans_multiscale_score(
    fit_context: np.ndarray,
    target: np.ndarray,
    query_context: np.ndarray,
    query_target: np.ndarray,
    counts: list[int],
    floor: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    scores = np.zeros(len(query_context))
    proposals = np.full(len(query_context), np.median(target))
    for count in sorted(set(counts)):
        if count == 1:
            fit_labels = np.zeros(len(fit_context), dtype=int)
            query_labels = np.zeros(len(query_context), dtype=int)
        else:
            model = KMeans(count, n_init=5, random_state=seed + count).fit(fit_context)
            fit_labels = model.labels_
            query_labels = model.predict(query_context)
        stats = {
            label: _robust_scale(target[fit_labels == label], floor)
            for label in range(count)
        }
        medians = np.asarray([stats[int(label)][0] for label in query_labels])
        scales = np.asarray([stats[int(label)][1] for label in query_labels])
        scores = np.maximum(scores, np.abs(query_target - medians) / scales)
        proposals = medians
    return scores, proposals


def inject_contextual_corruption(
    clean: np.ndarray, fold_ids: np.ndarray, rate: float, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    """Copy marginally valid values from a contextually distant local cluster."""

    rng = np.random.default_rng(seed)
    rows, columns = clean.shape
    target_count = int(round(rate * rows * columns))
    row_cap = max(1, int(np.ceil(0.10 * columns)))
    column_cap = max(1, int(np.ceil(0.05 * rows)))
    row_counts = np.zeros(rows, dtype=int)
    column_counts = np.zeros(columns, dtype=int)
    selected = []
    for flat in rng.permutation(rows * columns):
        row, column = divmod(int(flat), columns)
        if row_counts[row] >= row_cap or column_counts[column] >= column_cap:
            continue
        selected.append((row, column))
        row_counts[row] += 1
        column_counts[column] += 1
        if len(selected) == target_count:
            break
    corrupted = clean.copy()
    mask = np.zeros_like(clean, dtype=bool)
    for fold in np.unique(fold_ids):
        fold_rows = np.flatnonzero(fold_ids == fold)
        local_position = {int(row): position for position, row in enumerate(fold_rows)}
        for column in range(columns):
            targets = [row for row, feature in selected if feature == column and fold_ids[row] == fold]
            if not targets:
                continue
            context = np.delete(clean[fold_rows], column, axis=1)
            context = RobustScaler().fit_transform(context)
            cluster_count = min(4, max(2, len(fold_rows) // 15))
            labels = KMeans(cluster_count, n_init=5, random_state=seed + fold + column).fit_predict(context)
            medians = np.asarray([
                np.median(clean[fold_rows[labels == label], column])
                for label in range(cluster_count)
            ])
            for row in targets:
                own = int(labels[local_position[int(row)]])
                donor_cluster = int(np.argmax(np.abs(medians - medians[own])))
                donors = fold_rows[labels == donor_cluster]
                donor = int(rng.choice(donors))
                corrupted[row, column] = clean[donor, column]
                mask[row, column] = True
    return corrupted, mask


def _cross_fitted_scores(
    corrupted: np.ndarray, folds: list[tuple[np.ndarray, np.ndarray]], seed: int
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, float], float]:
    scores = {method: np.zeros_like(corrupted, dtype=float) for method in METHODS}
    proposals = {method: np.zeros_like(corrupted, dtype=float) for method in METHODS}
    runtimes = {method: 0.0 for method in METHODS}
    terminal_counts = []
    for fold_number, (fit_indices, query_indices) in enumerate(folds):
        scaler = RobustScaler().fit(corrupted[fit_indices])
        fit = scaler.transform(corrupted[fit_indices])
        query = scaler.transform(corrupted[query_indices])
        for column in range(corrupted.shape[1]):
            fit_context = np.delete(fit, column, axis=1)
            query_context = np.delete(query, column, axis=1)
            target = fit[:, column]
            query_target = query[:, column]
            global_iqr = float(np.subtract(*np.quantile(target, [0.75, 0.25])))
            floor = max(0.10 * global_iqr, 1e-3)
            min_leaf = max(10, int(np.ceil(0.05 * len(fit))))
            budget = min(16, max(4, len(fit) // 40))

            start = time.perf_counter()
            tree = build_context_tree(
                fit_context, budget, seed + 101 * fold_number + column, min_leaf
            )
            candidate_score, candidate_proposal = _hierarchical_score(
                tree, target, query_context, query_target, floor, True
            )
            runtimes["gb_surface_multiscale"] += time.perf_counter() - start
            scores["gb_surface_multiscale"][query_indices, column] = candidate_score
            proposals["gb_surface_multiscale"][query_indices, column] = candidate_proposal
            terminal_counts.append(len(tree.leaves))

            start = time.perf_counter()
            ablation_score, ablation_proposal = _hierarchical_score(
                tree, target, query_context, query_target, floor, False
            )
            runtimes["gb_center_multiscale"] += time.perf_counter() - start
            scores["gb_center_multiscale"][query_indices, column] = ablation_score
            proposals["gb_center_multiscale"][query_indices, column] = ablation_proposal

            start = time.perf_counter()
            counts = [len(cut) for cut in tree.cuts()]
            km_score, km_proposal = _kmeans_multiscale_score(
                fit_context,
                target,
                query_context,
                query_target,
                counts,
                floor,
                seed + 211 * fold_number + column,
            )
            runtimes["kmeans_multiscale"] += time.perf_counter() - start
            scores["kmeans_multiscale"][query_indices, column] = km_score
            proposals["kmeans_multiscale"][query_indices, column] = km_proposal

            start = time.perf_counter()
            median_leaf = int(np.median([len(tree.nodes[node].indices) for node in tree.leaves]))
            neighbors = min(len(fit), max(10, min(50, median_leaf)))
            neighbor_ids = NearestNeighbors(n_neighbors=neighbors).fit(fit_context).kneighbors(
                query_context, return_distance=False
            )
            neighbor_values = target[neighbor_ids]
            local_median = np.median(neighbor_values, axis=1)
            local_mad = 1.4826 * np.median(
                np.abs(neighbor_values - local_median[:, None]), axis=1
            )
            local_mad = np.maximum(local_mad, floor)
            runtimes["knn_context"] += time.perf_counter() - start
            scores["knn_context"][query_indices, column] = np.abs(query_target - local_median) / local_mad
            proposals["knn_context"][query_indices, column] = local_median

            start = time.perf_counter()
            regressor = DecisionTreeRegressor(
                max_leaf_nodes=max(2, len(tree.leaves)),
                min_samples_leaf=min_leaf,
                random_state=seed + 307 * fold_number + column,
            ).fit(fit_context, target)
            fit_residual = target - regressor.predict(fit_context)
            residual_scale = _robust_scale(fit_residual, floor)[1]
            tree_proposal = regressor.predict(query_context)
            runtimes["decision_tree"] += time.perf_counter() - start
            scores["decision_tree"][query_indices, column] = np.abs(query_target - tree_proposal) / residual_scale
            proposals["decision_tree"][query_indices, column] = tree_proposal

            start = time.perf_counter()
            global_median, global_scale = _robust_scale(target, floor)
            runtimes["global_robust"] += time.perf_counter() - start
            scores["global_robust"][query_indices, column] = np.abs(query_target - global_median) / global_scale
            proposals["global_robust"][query_indices, column] = global_median

            for method in METHODS:
                proposals[method][query_indices, column] = (
                    proposals[method][query_indices, column] * scaler.scale_[column]
                    + scaler.center_[column]
                )
    return scores, proposals, runtimes, float(np.mean(terminal_counts))


def _downstream(task, train_x, train_y, test_x, test_y, seed):
    scaler = StandardScaler().fit(train_x)
    train = scaler.transform(train_x)
    test = scaler.transform(test_x)
    if task == "classification":
        model = LogisticRegression(max_iter=2000, random_state=seed).fit(train, train_y)
        prediction = model.predict(test)
        return {
            "primary": float(balanced_accuracy_score(test_y, prediction)),
            "balanced_accuracy": float(balanced_accuracy_score(test_y, prediction)),
            "macro_f1": float(f1_score(test_y, prediction, average="macro")),
        }
    model = Ridge(alpha=1.0).fit(train, train_y)
    prediction = model.predict(test)
    return {
        "primary": -float(mean_squared_error(test_y, prediction) ** 0.5),
        "rmse": float(mean_squared_error(test_y, prediction) ** 0.5),
        "r2": float(r2_score(test_y, prediction)),
    }


def evaluate_cell_cleaning(
    dataset: str, seed: int, corruption_rate: float = 0.03, n_splits: int = 5
) -> dict[str, object]:
    features, target, task = load_dataset(dataset)
    stratify = target
    if task == "regression":
        quantiles = np.quantile(target, [0.2, 0.4, 0.6, 0.8])
        stratify = np.digitize(target, quantiles)
    train_x, test_x, train_y, test_y = train_test_split(
        features,
        target,
        test_size=0.30,
        random_state=seed,
        stratify=stratify,
    )
    fold_pairs = list(KFold(n_splits, shuffle=True, random_state=seed + 17).split(train_x))
    fold_ids = np.empty(len(train_x), dtype=int)
    for fold, (_, query_indices) in enumerate(fold_pairs):
        fold_ids[query_indices] = fold
    corrupted, mask = inject_contextual_corruption(
        train_x, fold_ids, corruption_rate, seed + 1009
    )
    scores, proposals, runtimes, mean_terminal_count = _cross_fitted_scores(
        corrupted, fold_pairs, seed
    )
    clean_downstream = _downstream(task, train_x, train_y, test_x, test_y, seed)
    dirty_downstream = _downstream(task, corrupted, train_y, test_x, test_y, seed)
    scale = np.subtract(*np.quantile(train_x, [0.75, 0.25], axis=0))
    scale = np.maximum(scale, 1e-6)
    review_count = int(mask.sum())
    rows = []
    for method in METHODS:
        flat_scores = scores[method].ravel()
        selected_flat = np.argpartition(flat_scores, -review_count)[-review_count:]
        selected = np.zeros_like(flat_scores, dtype=bool)
        selected[selected_flat] = True
        selected = selected.reshape(mask.shape)
        repaired = corrupted.copy()
        repaired[selected] = proposals[method][selected]
        normalized_error = np.abs(repaired - train_x) / scale[None, :]
        downstream = _downstream(task, repaired, train_y, test_x, test_y, seed)
        rows.append(
            {
                "method": method,
                "cell_auprc": float(average_precision_score(mask.ravel(), flat_scores)),
                "precision_at_review_budget": float(mask[selected].mean()),
                "normalized_mae_all_cells": float(normalized_error.mean()),
                "normalized_mae_corrupted_cells": float(normalized_error[mask].mean()),
                "clean_cell_edit_rate": float((selected & ~mask).sum() / (~mask).sum()),
                "runtime_seconds": runtimes[method],
                "downstream": downstream,
                "downstream_delta_vs_dirty": downstream["primary"] - dirty_downstream["primary"],
            }
        )
    return {
        "dataset": dataset,
        "task": task,
        "seed": seed,
        "corruption_rate": float(mask.mean()),
        "corrupted_cells": int(mask.sum()),
        "mean_terminal_count": mean_terminal_count,
        "clean_downstream": clean_downstream,
        "dirty_downstream": dirty_downstream,
        "methods": rows,
    }
