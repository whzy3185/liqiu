from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import pairwise_distances

from baselines.gbc import GranularBallClassifier


@dataclass(frozen=True)
class PrototypeSet:
    method: str
    centers: np.ndarray
    radii: np.ndarray
    labels: np.ndarray
    counts: np.ndarray


def client_partitions(y: np.ndarray, n_clients: int, seed: int, alpha: float = 0.5) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    clients: list[list[int]] = [[] for _ in range(n_clients)]
    for label in np.unique(y):
        indices = rng.permutation(np.flatnonzero(y == label))
        proportions = rng.dirichlet(np.full(n_clients, alpha))
        cuts = np.r_[0, np.cumsum((proportions * len(indices)).astype(int))]
        cuts[-1] = len(indices)
        for client in range(n_clients):
            clients[client].extend(indices[cuts[client] : cuts[client + 1]].tolist())
    # Empty clients would make the communication comparison ill-defined.
    empty = [i for i, values in enumerate(clients) if not values]
    for client in empty:
        donor = max(range(n_clients), key=lambda i: len(clients[i]))
        clients[client].append(clients[donor].pop())
    return [np.asarray(sorted(values), dtype=int) for values in clients]


def summarize_clients(
    X: np.ndarray,
    y: np.ndarray,
    partitions: list[np.ndarray],
    seed: int,
    purity: float = 0.9,
) -> dict[str, PrototypeSet]:
    collected: dict[str, list[PrototypeSet]] = {name: [] for name in ("raw", "kmeans", "microcluster", "granular_ball")}
    for client, indices in enumerate(partitions):
        local_X, local_y = X[indices], y[indices]
        collected["raw"].append(
            PrototypeSet("raw", local_X, np.zeros(len(indices)), local_y, np.ones(len(indices), dtype=int))
        )
        gbc = GranularBallClassifier(purity=purity, min_samples=2, random_state=seed + client).fit(local_X, local_y)
        k = len(gbc.balls_)
        collected["granular_ball"].append(
            PrototypeSet(
                "granular_ball",
                np.vstack([ball.center for ball in gbc.balls_]),
                np.asarray([ball.radius for ball in gbc.balls_]),
                np.asarray([ball.label for ball in gbc.balls_]),
                np.asarray([len(ball.members) for ball in gbc.balls_]),
            )
        )
        collected["kmeans"].append(_cluster_summary("kmeans", KMeans(n_clusters=k, n_init=10, random_state=seed + client), local_X, local_y))
        collected["microcluster"].append(
            _cluster_summary(
                "microcluster",
                MiniBatchKMeans(n_clusters=k, n_init=5, batch_size=min(256, len(local_X)), random_state=seed + client),
                local_X,
                local_y,
            )
        )
    return {method: _concatenate(parts) for method, parts in collected.items()}


def evaluate_prototypes(prototypes: PrototypeSet, X_test: np.ndarray, y_test: np.ndarray, n_train: int) -> dict[str, float]:
    distances = pairwise_distances(X_test, prototypes.centers)
    if prototypes.method == "granular_ball":
        distances = distances - prototypes.radii[None, :]
    prediction = prototypes.labels[np.argmin(distances, axis=1)]
    accuracy = float(np.mean(prediction == y_test))
    dimension = prototypes.centers.shape[1]
    m = len(prototypes.centers)
    if prototypes.method == "raw":
        bytes_sent = m * (dimension + 1) * 8
    else:
        # center, radius, count, and one majority-label statistic.
        bytes_sent = m * (dimension + 3) * 8
    scalar_count = m * dimension
    return {
        "accuracy": accuracy,
        "m_over_n": float(m / n_train),
        "communication_bytes": float(bytes_sent),
        "secure_additions_estimate": float(scalar_count),
        "secure_multiplications_estimate": float(scalar_count),
        "ciphertext_count_estimate": float(np.ceil(scalar_count / 4096)),
        "n_prototypes": float(m),
    }


def _cluster_summary(method: str, model, X: np.ndarray, y: np.ndarray) -> PrototypeSet:
    assignment = model.fit_predict(X)
    centers, radii, labels, counts = [], [], [], []
    for group in np.unique(assignment):
        indices = np.flatnonzero(assignment == group)
        center = X[indices].mean(axis=0)
        values, frequencies = np.unique(y[indices], return_counts=True)
        centers.append(center)
        radii.append(np.linalg.norm(X[indices] - center, axis=1).mean())
        labels.append(values[np.argmax(frequencies)])
        counts.append(len(indices))
    return PrototypeSet(method, np.asarray(centers), np.asarray(radii), np.asarray(labels), np.asarray(counts))


def _concatenate(parts: list[PrototypeSet]) -> PrototypeSet:
    return PrototypeSet(
        parts[0].method,
        np.vstack([part.centers for part in parts]),
        np.concatenate([part.radii for part in parts]),
        np.concatenate([part.labels for part in parts]),
        np.concatenate([part.counts for part in parts]),
    )

