"""Learnable anisotropic GB regions for cross-view recovery and classification."""

from __future__ import annotations

import time

import numpy as np
import torch
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml, load_breast_cancer, load_digits, load_wine
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch import nn


DATASETS = ("satimage", "digits", "breast_cancer", "wine")
METHODS = ("anisotropic_gb", "isotropic_prototype", "mlp_imputer", "fixed_kmeans", "ridge", "visible_only")
MISSING_RATES = (0.20, 0.40, 0.60)


def _load(dataset, seed, max_samples=2400):
    if dataset == "satimage":
        bundle = fetch_openml(data_id=182, as_frame=False, parser="auto")
        features = np.asarray(bundle.data, float)
        labels = LabelEncoder().fit_transform(bundle.target)
    elif dataset == "digits":
        bundle = load_digits()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "breast_cancer":
        bundle = load_breast_cancer()
        features, labels = bundle.data.astype(float), bundle.target
    elif dataset == "wine":
        bundle = load_wine()
        features, labels = bundle.data.astype(float), bundle.target
    else:
        raise ValueError(dataset)
    if len(labels) > max_samples:
        selected, _ = train_test_split(
            np.arange(len(labels)), train_size=max_samples, stratify=labels, random_state=seed
        )
        features, labels = features[selected], labels[selected]
    split = features.shape[1] // 2
    return features[:, :split], features[:, split:], np.asarray(labels, int)


class PrototypeImputer(nn.Module):
    def __init__(self, centers, prototypes, classes, anisotropic):
        super().__init__()
        self.centers = nn.Parameter(torch.tensor(centers, dtype=torch.float32))
        self.prototypes = nn.Parameter(torch.tensor(prototypes, dtype=torch.float32))
        scale_shape = centers.shape if anisotropic else (len(centers), 1)
        self.log_scale = nn.Parameter(torch.zeros(scale_shape))
        self.classifier = nn.Linear(centers.shape[1] + prototypes.shape[1], classes)

    def recover(self, view_a):
        scale = torch.nn.functional.softplus(self.log_scale) + 0.05
        distance = torch.sum(((view_a[:, None, :] - self.centers[None, :, :]) / scale) ** 2, dim=2)
        assignment = torch.softmax(-distance, dim=1)
        return assignment @ self.prototypes

    def forward(self, view_a):
        recovered = self.recover(view_a)
        return self.classifier(torch.cat([view_a, recovered], dim=1)), recovered


class MLPImputer(nn.Module):
    def __init__(self, input_size, output_size, classes):
        super().__init__()
        hidden = max(16, min(64, 2 * input_size))
        self.imputer = nn.Sequential(nn.Linear(input_size, hidden), nn.ReLU(), nn.Linear(hidden, output_size))
        self.classifier = nn.Linear(input_size + output_size, classes)

    def forward(self, view_a):
        recovered = self.imputer(view_a)
        return self.classifier(torch.cat([view_a, recovered], dim=1)), recovered


def _device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _train_neural(model, train_a, train_b, train_y, epochs, seed, device):
    torch.manual_seed(seed)
    model = model.to(device)
    a = torch.tensor(train_a, dtype=torch.float32, device=device)
    b = torch.tensor(train_b, dtype=torch.float32, device=device)
    y = torch.tensor(train_y, dtype=torch.long, device=device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    start = time.perf_counter()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits, recovered = model(a)
        loss = nn.functional.cross_entropy(logits, y) + 0.5 * nn.functional.mse_loss(recovered, b)
        loss.backward()
        optimizer.step()
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        torch.mps.synchronize()
    return model, time.perf_counter() - start


def _neural_predict(model, test_a, device):
    model.eval()
    with torch.no_grad():
        a = torch.tensor(test_a, dtype=torch.float32, device=device)
        logits, recovered = model(a)
        return logits.cpu().numpy(), recovered.cpu().numpy()


def _classifier_metrics(train_a, train_b, train_y, test_a, test_b, test_y, recovered, rates, seed):
    classifier = LogisticRegression(max_iter=2000, random_state=seed).fit(
        np.column_stack([train_a, train_b]), train_y
    )
    order = np.random.default_rng(seed + 99).permutation(len(test_y))
    rows = []
    for rate in rates:
        missing = np.zeros(len(test_y), dtype=bool)
        missing[order[: int(round(rate * len(test_y)))]] = True
        merged = test_b.copy()
        merged[missing] = recovered[missing]
        prediction = classifier.predict(np.column_stack([test_a, merged]))
        scale = max(float(np.std(test_b[missing])), 1e-9)
        rows.append(
            {
                "missing_rate": rate,
                "imputation_nrmse": float(
                    np.sqrt(np.mean((recovered[missing] - test_b[missing]) ** 2)) / scale
                ),
                "accuracy": float(accuracy_score(test_y, prediction)),
                "missing_item_accuracy": float(accuracy_score(test_y[missing], prediction[missing])),
            }
        )
    return rows


def evaluate_learnable_cross_view(dataset: str, seed: int, epochs: int = 80):
    view_a, view_b, labels = _load(dataset, seed)
    train_a, test_a, train_b, test_b, train_y, test_y = train_test_split(
        view_a, view_b, labels, test_size=0.30, stratify=labels, random_state=seed
    )
    scaler_a, scaler_b = StandardScaler().fit(train_a), StandardScaler().fit(train_b)
    train_a, test_a = scaler_a.transform(train_a), scaler_a.transform(test_a)
    train_b, test_b = scaler_b.transform(train_b), scaler_b.transform(test_b)
    classes = len(np.unique(labels))
    count = min(12, max(4, len(train_a) // 100))
    kmeans = KMeans(count, n_init=10, random_state=seed).fit(train_a)
    centers = kmeans.cluster_centers_
    prototypes = np.vstack([train_b[kmeans.labels_ == label].mean(axis=0) for label in range(count)])
    device = _device()
    outputs = {}

    for method, anisotropic in (("anisotropic_gb", True), ("isotropic_prototype", False)):
        torch.manual_seed(seed + METHODS.index(method))
        model, seconds = _train_neural(
            PrototypeImputer(centers, prototypes, classes, anisotropic),
            train_a,
            train_b,
            train_y,
            epochs,
            seed + METHODS.index(method),
            device,
        )
        _, recovered = _neural_predict(model, test_a, device)
        outputs[method] = (recovered, seconds, sum(parameter.numel() for parameter in model.parameters()))

    torch.manual_seed(seed + 10)
    model, seconds = _train_neural(
        MLPImputer(train_a.shape[1], train_b.shape[1], classes),
        train_a,
        train_b,
        train_y,
        epochs,
        seed + 10,
        device,
    )
    _, recovered = _neural_predict(model, test_a, device)
    outputs["mlp_imputer"] = (recovered, seconds, sum(parameter.numel() for parameter in model.parameters()))

    outputs["fixed_kmeans"] = (prototypes[kmeans.predict(test_a)], 0.0, centers.size + prototypes.size)
    start = time.perf_counter()
    outputs["ridge"] = (Ridge(alpha=1.0).fit(train_a, train_b).predict(test_a), time.perf_counter() - start, train_a.shape[1] * train_b.shape[1])
    outputs["visible_only"] = (np.zeros_like(test_b), 0.0, 0)

    rows = []
    for method in METHODS:
        recovered, seconds, parameters = outputs[method]
        for point in _classifier_metrics(
            train_a, train_b, train_y, test_a, test_b, test_y, recovered, MISSING_RATES, seed
        ):
            rows.append(
                {
                    "method": method,
                    "training_seconds": seconds,
                    "parameters": parameters,
                    "device": str(device),
                    **point,
                }
            )
    return {"dataset": dataset, "seed": seed, "epochs": epochs, "regions": count, "device": str(device), "frontier": rows}
