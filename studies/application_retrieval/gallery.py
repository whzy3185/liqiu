"""Fixed-slot visual and spectral gallery compression for exact reranking."""

from __future__ import annotations

import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_digits
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


DATASETS = ("satimage", "satellite", "covertype", "digits")
METHODS = ("granular_ball", "kmeans", "kcenter", "axis_tree", "random", "full")
FRACTIONS = (0.05, 0.10, 0.20)


def _load(dataset: str, seed: int, max_samples: int = 2400):
    if dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
        metadata = {"source": "sklearn", "md5": None}
    else:
        ids = {"satimage": 182, "satellite": 40900, "covertype": 1596}
        bundle = fetch_openml(data_id=ids[dataset], as_frame=False, parser="auto")
        features = np.asarray(bundle.data, float)
        labels = LabelEncoder().fit_transform(bundle.target)
        metadata = {
            "source": f"openml-{ids[dataset]}",
            "md5": bundle.details.get("md5_checksum"),
        }
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    return features, np.asarray(labels, int), metadata


def _embedding(gallery: np.ndarray, query: np.ndarray):
    scaler = StandardScaler().fit(gallery)
    gallery = scaler.transform(gallery)
    query = scaler.transform(query)
    dimensions = min(16, gallery.shape[1], len(gallery) - 1)
    pca = PCA(n_components=dimensions, random_state=0).fit(gallery)
    return pca.transform(gallery), pca.transform(query)


def _medoid(features: np.ndarray, indices: np.ndarray) -> int:
    center = features[indices].mean(axis=0)
    return int(indices[np.argmin(np.linalg.norm(features[indices] - center, axis=1))])


def _gb_select(features, count, seed):
    groups = [np.arange(len(features))]
    split_round = 0
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            local = features[indices]
            center = local.mean(axis=0)
            score = len(indices) * float(np.median(np.linalg.norm(local - center, axis=1)))
            candidates.append((score, position, indices))
        if not candidates:
            break
        _, position, indices = max(candidates)
        labels = KMeans(2, n_init=3, random_state=seed + split_round).fit_predict(features[indices])
        children = [indices[labels == label] for label in (0, 1)]
        if min(map(len, children)) == 0:
            break
        groups[position : position + 1] = children
        split_round += 1
    return np.asarray([_medoid(features, indices) for indices in groups[:count]])


def _kmeans_select(features, count, seed):
    labels = KMeans(count, n_init=5, random_state=seed).fit_predict(features)
    return np.asarray([_medoid(features, np.flatnonzero(labels == label)) for label in range(count)])


def _kcenter_order(features, count, seed):
    first = int(np.random.default_rng(seed).integers(len(features)))
    selected = [first]
    distances = np.linalg.norm(features - features[first], axis=1)
    for _ in range(1, count):
        choice = int(np.argmax(distances))
        selected.append(choice)
        distances = np.minimum(distances, np.linalg.norm(features - features[choice], axis=1))
        distances[selected] = -1
    return np.asarray(selected)


def _axis_select(features, count):
    groups = [np.arange(len(features))]
    while len(groups) < count:
        candidates = []
        for position, indices in enumerate(groups):
            if len(indices) < 2:
                continue
            variance = np.var(features[indices], axis=0)
            candidates.append((float(variance.max() * len(indices)), position, indices, int(np.argmax(variance))))
        if not candidates:
            break
        _, position, indices, feature = max(candidates)
        ordered = indices[np.argsort(features[indices, feature])]
        middle = len(ordered) // 2
        groups[position : position + 1] = [ordered[:middle], ordered[middle:]]
    return np.asarray([_medoid(features, indices) for indices in groups[:count]])


def _retrieval_metrics(query_x, query_y, gallery_x, gallery_y, full_counts, rare_classes, k=10):
    start = time.perf_counter()
    distances = np.maximum(
        np.sum(query_x * query_x, axis=1)[:, None]
        + np.sum(gallery_x * gallery_x, axis=1)[None, :]
        - 2 * query_x @ gallery_x.T,
        0,
    )
    top = np.argpartition(distances, min(k, len(gallery_x)) - 1, axis=1)[:, : min(k, len(gallery_x))]
    top_distances = np.take_along_axis(distances, top, axis=1)
    order = np.argsort(top_distances, axis=1)
    top = np.take_along_axis(top, order, axis=1)
    query_seconds = time.perf_counter() - start
    relevance = gallery_y[top] == query_y[:, None]
    precision = np.cumsum(relevance, axis=1) / np.arange(1, relevance.shape[1] + 1)
    denominators = np.minimum(np.asarray([full_counts[label] for label in query_y]), relevance.shape[1])
    ap = np.sum(precision * relevance, axis=1) / np.maximum(denominators, 1)
    hit = relevance.any(axis=1)
    rare = np.isin(query_y, rare_classes)
    return {
        "map_at_10": float(ap.mean()),
        "hit_at_10": float(hit.mean()),
        "rare_hit_at_10": float(hit[rare].mean()) if rare.any() else None,
        "precision_at_10": float(relevance.mean()),
        "query_seconds": query_seconds,
        "distance_computations": int(len(query_x) * len(gallery_x)),
    }


def evaluate_gallery_retrieval(dataset: str, seed: int):
    features, labels, metadata = _load(dataset, seed)
    gallery_x, query_x, gallery_y, query_y = train_test_split(
        features, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    gallery_x, query_x = _embedding(gallery_x, query_x)
    counts = np.bincount(gallery_y)
    rare_classes = np.argsort(counts)[: max(1, len(counts) // 3)]
    maximum = int(np.ceil(max(FRACTIONS) * len(gallery_x)))
    start = time.perf_counter()
    kcenter = _kcenter_order(gallery_x, maximum, seed + 10)
    kcenter_seconds = time.perf_counter() - start
    random_order = np.random.default_rng(seed + 20).permutation(len(gallery_x))[:maximum]
    rows = []
    for fraction in FRACTIONS:
        count = int(np.ceil(fraction * len(gallery_x)))
        selections = {}
        timings = {}
        for method, selector in (
            ("granular_ball", lambda: _gb_select(gallery_x, count, seed + count)),
            ("kmeans", lambda: _kmeans_select(gallery_x, count, seed + count)),
            ("axis_tree", lambda: _axis_select(gallery_x, count)),
        ):
            start = time.perf_counter()
            selections[method] = selector()
            timings[method] = time.perf_counter() - start
        selections["kcenter"] = kcenter[:count]
        selections["random"] = random_order[:count]
        selections["full"] = np.arange(len(gallery_x))
        timings["kcenter"] = kcenter_seconds * count / maximum
        timings["random"] = 0.0
        timings["full"] = 0.0
        for method in METHODS:
            selected = selections[method]
            metrics = _retrieval_metrics(
                query_x,
                query_y,
                gallery_x[selected],
                gallery_y[selected],
                counts,
                rare_classes,
            )
            rows.append(
                {
                    "method": method,
                    "fraction": fraction if method != "full" else 1.0,
                    "slots": len(selected),
                    "selection_seconds": timings[method],
                    **metrics,
                }
            )
    return {
        "dataset": dataset,
        "seed": seed,
        "gallery_size": len(gallery_x),
        "query_size": len(query_x),
        "classes": len(counts),
        "rare_classes": rare_classes.tolist(),
        "metadata": metadata,
        "frontier": rows,
    }
