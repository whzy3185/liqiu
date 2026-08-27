"""A3 refinement membership attack with mandatory matched-k KMeans controls."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.metrics import pairwise_distances
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from studies.risk_granularity.tree import GranulationTree


THRESHOLDS = (0.70, 0.80, 0.90, 0.95, 0.99)
OPENML = {"ionosphere": 59, "sonar": 40, "banknote": 1462}


@dataclass(frozen=True)
class Release:
    method: str
    level: str
    centers: np.ndarray
    radii: np.ndarray
    sizes: np.ndarray
    purities: np.ndarray
    labels: np.ndarray
    members: tuple[np.ndarray, ...]
    depths: np.ndarray
    parent_ids: np.ndarray


def load_dataset(name: str, cache: Path) -> tuple[np.ndarray, np.ndarray, str]:
    if name == "breast_cancer":
        bunch = load_breast_cancer()
        return np.asarray(bunch.data, float), np.asarray(bunch.target, int), "sklearn.load_breast_cancer"
    if name == "wine":
        bunch = load_wine()
        return np.asarray(bunch.data, float), np.asarray(bunch.target, int), "sklearn.load_wine"
    if name == "digits":
        bunch = load_digits()
        return np.asarray(bunch.data, float), np.asarray(bunch.target, int), "sklearn.load_digits"
    if name in {"sonar", "spambase"}:
        from ucimlrepo import fetch_ucirepo
        dataset_id = {"sonar": 151, "spambase": 94}[name]
        bunch = fetch_ucirepo(id=dataset_id)
        x = np.asarray(bunch.data.features, float)
        y = LabelEncoder().fit_transform(np.asarray(bunch.data.targets).reshape(-1))
        return x, y, f"UCI id={dataset_id} via ucimlrepo"
    if name not in OPENML:
        raise ValueError(f"Unknown dataset {name}")
    bunch = fetch_openml(data_id=OPENML[name], as_frame=False, data_home=str(cache), parser="auto")
    return np.asarray(bunch.data, float), LabelEncoder().fit_transform(bunch.target), f"OpenML data_id={OPENML[name]}"


def load_grouped_dataset(name: str, cache: Path | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Load a public dataset whose entity ID must remain split-disjoint."""
    if name != "musk1":
        raise ValueError(f"Unknown grouped dataset {name}")
    cache_file = None if cache is None else cache / "musk1_grouped.npz"
    if cache_file is not None and cache_file.exists():
        data = np.load(cache_file, allow_pickle=False)
        return data["x"], data["y"], data["groups"], "UCI id=74 cached official retrieval; molecule_name group split"
    from ucimlrepo import fetch_ucirepo
    bunch = fetch_ucirepo(id=74)
    frame = bunch.data.features
    groups = frame["molecule_name"].astype(str).to_numpy()
    x = np.asarray(frame.drop(columns=["molecule_name", "conformation_name"]), dtype=float)
    y = LabelEncoder().fit_transform(np.asarray(bunch.data.targets).reshape(-1))
    if cache_file is not None:
        cache.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_file, x=x, y=y, groups=np.asarray(groups, dtype="U"))
    return x, y, groups, "UCI id=74 via ucimlrepo; molecule_name group split"


def split_standardize(x: np.ndarray, y: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_member, x_nonmember, y_member, y_nonmember = train_test_split(x, y, test_size=0.5, stratify=y, random_state=seed)
    scaler = StandardScaler().fit(x_member)
    return scaler.transform(x_member), y_member, scaler.transform(x_nonmember), y_nonmember


def split_standardize_groups(x: np.ndarray, y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    splitter = StratifiedGroupKFold(n_splits=2, shuffle=True, random_state=seed)
    member_index, nonmember_index = next(splitter.split(x, y, groups))
    if set(groups[member_index]) & set(groups[nonmember_index]):
        raise RuntimeError("group split leaked an entity across member/non-member sets")
    scaler = StandardScaler().fit(x[member_index])
    return scaler.transform(x[member_index]), y[member_index], scaler.transform(x[nonmember_index]), y[nonmember_index]


def _tree_metadata(tree: GranulationTree) -> dict[int, tuple[int, int | None, int]]:
    metadata: dict[int, tuple[int, int | None, int]] = {}
    next_id = 0
    def visit(node, parent: int | None, depth: int) -> None:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        metadata[id(node)] = (node_id, parent, depth)
        for child in node.children:
            visit(child, node_id, depth + 1)
    visit(tree.root, None, 0)
    return metadata


def gb_release(tree: GranulationTree, x: np.ndarray, threshold: float, level: str) -> Release:
    metadata = _tree_metadata(tree)
    nodes = tree.cut(threshold)
    members = tuple(np.asarray(node.indices, dtype=np.int64) for node in nodes)
    radii = np.array([np.linalg.norm(x[m] - node.center, axis=1).mean() for m, node in zip(members, nodes)], dtype=float)
    return Release("granular_ball", level, np.vstack([n.center for n in nodes]), radii, np.array([len(m) for m in members]), np.array([n.purity for n in nodes]), np.array([n.label for n in nodes]), members, np.array([metadata[id(n)][2] for n in nodes]), np.array([metadata[id(n)][1] if metadata[id(n)][1] is not None else -1 for n in nodes]))


def kmeans_release(x: np.ndarray, y: np.ndarray, k: int, seed: int, level: str) -> Release:
    labels = KMeans(n_clusters=k, n_init="auto", random_state=seed).fit_predict(x)
    members = tuple(np.flatnonzero(labels == cluster) for cluster in np.unique(labels))
    centers, radii, purity, majority = [], [], [], []
    for member in members:
        center = x[member].mean(axis=0)
        values, counts = np.unique(y[member], return_counts=True)
        centers.append(center)
        radii.append(np.linalg.norm(x[member] - center, axis=1).mean())
        purity.append(counts.max() / len(member))
        majority.append(values[np.argmax(counts)])
    return Release("matched_kmeans", level, np.asarray(centers), np.asarray(radii), np.array([len(m) for m in members]), np.asarray(purity), np.asarray(majority), members, np.full(k, -1, dtype=int), np.full(k, -1, dtype=int))


def attack_features(release: Release, queries: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    distances = pairwise_distances(queries, release.centers)
    order = np.argsort(distances, axis=1)
    nearest = order[:, 0]
    first = distances[np.arange(len(queries)), nearest]
    second = distances[np.arange(len(queries)), order[:, min(1, distances.shape[1] - 1)]]
    nearest_distances = np.take_along_axis(distances, order[:, : min(3, distances.shape[1])], axis=1)
    features = [first, second - first, nearest_distances.mean(axis=1)]
    if release.level in ("release_2", "release_3"):
        radius = np.maximum(release.radii[nearest], 1e-12)
        features.extend([first / radius, release.radii[nearest], (distances <= release.radii[None, :]).sum(axis=1)])
    if release.level == "release_3":
        features.extend([np.log1p(release.sizes[nearest]), release.purities[nearest]])
        one_hot = (release.labels[nearest, None] == np.unique(release.labels)[None, :]).astype(float)
        features.append(one_hot)
    return np.column_stack(features), nearest


def _tpr_at_fpr(y: np.ndarray, score: np.ndarray, target: float) -> float:
    fpr, tpr, _ = roc_curve(y, score)
    return float(tpr[fpr <= target].max()) if np.any(fpr <= target) else 0.0


def attack_metrics(release: Release, x_member: np.ndarray, x_nonmember: np.ndarray, seed: int, attack: str) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    count = min(len(x_member), len(x_nonmember))
    queries = np.vstack([x_member[:count], x_nonmember[:count]])
    target = np.r_[np.ones(count, dtype=int), np.zeros(count, dtype=int)]
    features, nearest = attack_features(release, queries)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced")) if attack == "logistic" else RandomForestClassifier(n_estimators=200, min_samples_leaf=2, class_weight="balanced", n_jobs=1, random_state=seed)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    score = cross_val_predict(model, features, target, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
    values = {"roc_auc": float(roc_auc_score(target, score)), "pr_auc": float(average_precision_score(target, score)), "tpr_at_1pct_fpr": _tpr_at_fpr(target, score, 0.01), "tpr_at_0_1pct_fpr": _tpr_at_fpr(target, score, 0.001) if count >= 1000 else float("nan")}
    return values, score, nearest


def trajectory_rows(release: Release, dataset: str, seed: int, threshold: float) -> list[dict[str, object]]:
    rows = []
    for ball_id, member in enumerate(release.members):
        parent = int(release.parent_ids[ball_id])
        rows.append({"dataset": dataset, "seed": seed, "threshold": threshold, "method": release.method, "ball_id": ball_id, "center": json.dumps(release.centers[ball_id].tolist()), "radius": release.radii[ball_id], "size": len(member), "majority_label": release.labels[ball_id], "purity": release.purities[ball_id], "member_indices": json.dumps(member.tolist()), "parent_ball": None if parent < 0 else parent, "refinement_depth": int(release.depths[ball_id])})
    return rows


def _flip_training_labels(y: np.ndarray, fraction: float, seed: int) -> np.ndarray:
    if fraction <= 0:
        return y
    rng = np.random.default_rng(seed)
    out = y.copy()
    positions = rng.choice(len(out), size=int(round(len(out) * fraction)), replace=False)
    classes = np.unique(out)
    for position in positions:
        alternatives = classes[classes != out[position]]
        out[position] = rng.choice(alternatives)
    return out


def run_arrays(dataset: str, x: np.ndarray, y: np.ndarray, source: str, seed: int, context: dict[str, object] | None = None, training_label_noise: float = 0.0, groups: np.ndarray | None = None) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    context = {} if context is None else context
    x_member, y_member, x_nonmember, _ = split_standardize(x, y, seed) if groups is None else split_standardize_groups(x, y, groups, seed)
    y_member = _flip_training_labels(y_member, training_label_noise, seed * 7919 + 17)
    tree = GranulationTree(random_state=211 + seed, split_method="kmeans").fit(x_member, y_member)
    results: list[dict[str, object]] = []
    balls: list[dict[str, object]] = []
    for threshold in THRESHOLDS:
        gb_base = gb_release(tree, x_member, threshold, "release_1")
        km_base = kmeans_release(x_member, y_member, len(gb_base.members), seed, "release_1")
        for level in ("release_1", "release_2", "release_3"):
            gb = replace(gb_base, level=level)
            km = replace(km_base, level=level)
            for release in (gb, km):
                balls.extend(trajectory_rows(release, dataset, seed, threshold))
                for attack in ("logistic", "random_forest"):
                    metric, _, _ = attack_metrics(release, x_member, x_nonmember, seed, attack)
                    sizes = release.sizes
                    results.append({"dataset": dataset, "source": source, "seed": seed, "threshold": threshold, "release": level, "method": release.method, "attack": attack, "n": len(x), "d": x.shape[1], "classes": len(np.unique(y)), "number_of_balls": len(sizes), "mean_ball_size": float(sizes.mean()), "median_ball_size": float(np.median(sizes)), "min_ball_size": int(sizes.min()), "max_ball_size": int(sizes.max()), "singleton_count": int((sizes == 1).sum()), "fraction_size_le_2": float((sizes <= 2).mean()), "fraction_size_le_5": float((sizes <= 5).mean()), "mean_radius": float(release.radii.mean()), "median_radius": float(np.median(release.radii)), "purity_mean": float(release.purities.mean()), "purity_median": float(np.median(release.purities)), "purity_q25": float(np.quantile(release.purities, .25)), "purity_q75": float(np.quantile(release.purities, .75)), **context, **metric})
    return results, balls, {"dataset": dataset, "seed": seed, "n": len(x), "d": x.shape[1], "classes": len(np.unique(y)), "source": source, **context}


def run_seed(dataset: str, seed: int, cache: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    x, y, source = load_dataset(dataset, cache)
    return run_arrays(dataset, x, y, source, seed)


def synthetic_regime(*, n: int, dimension: int, separation: float, density_ratio: float, minority_fraction: float, modes: int, redundant_fraction: float, label_noise: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Controlled Gaussian-mixture regime; labels are the only generated target."""
    rng = np.random.default_rng(seed)
    n_minority = int(round(n * minority_fraction))
    n_majority = n - n_minority
    signal_dimensions = max(2, int(round(dimension * (1 - redundant_fraction))))
    majority = rng.normal(0, 1.0, size=(n_majority, signal_dimensions))
    minority_parts = np.array_split(np.arange(n_minority), modes)
    minority = np.empty((n_minority, signal_dimensions))
    for mode_id, positions in enumerate(minority_parts):
        center = np.zeros(signal_dimensions)
        center[0] = separation
        if signal_dimensions > 1:
            center[1] = (mode_id - (modes - 1) / 2) * separation * 0.75
        minority[positions] = rng.normal(center, 1 / density_ratio, size=(len(positions), signal_dimensions))
    x = np.vstack([majority, minority])
    y = np.r_[np.zeros(n_majority, dtype=int), np.ones(n_minority, dtype=int)]
    redundant_dimensions = dimension - signal_dimensions
    if redundant_dimensions:
        source_columns = rng.integers(0, signal_dimensions, size=redundant_dimensions)
        redundant = x[:, source_columns] + rng.normal(0, 0.02, size=(n, redundant_dimensions))
        x = np.column_stack([x, redundant])
    if label_noise:
        flip = rng.choice(n, size=int(round(n * label_noise)), replace=False)
        y[flip] = 1 - y[flip]
    order = rng.permutation(n)
    return x[order], y[order]
