"""Adapters for auditable structure smoke tests against unvendored author code."""

from __future__ import annotations

import importlib.util
import random
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

import numpy as np
from sklearn.datasets import make_moons


ROOT = Path(__file__).resolve().parents[2]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load upstream module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_commit(path: Path, expected: str) -> None:
    repository = path.parent
    while repository != repository.parent and not (repository / ".git").exists():
        repository = repository.parent
    actual = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repository, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout.strip()
    if actual != expected:
        raise RuntimeError(f"upstream commit mismatch: expected {expected}, got {actual}")


def _purity(ball: np.ndarray) -> float:
    _, counts = np.unique(ball[:, 0], return_counts=True)
    return float(counts.max() / len(ball)) if len(ball) else 1.0


def _resubstitution_accuracy(balls: Sequence[np.ndarray], data: np.ndarray) -> float:
    centers = np.vstack([ball[:, 1:].mean(axis=0) for ball in balls])
    labels = np.array([
        np.unique(ball[:, 0], return_counts=True)[0][np.argmax(np.unique(ball[:, 0], return_counts=True)[1])]
        for ball in balls
    ])
    distances = ((data[:, None, 1:] - centers[None, :, :]) ** 2).sum(axis=2)
    predicted = labels[np.argmin(distances, axis=1)]
    return float(np.mean(predicted == data[:, 0]))


def _original(module, data: np.ndarray, threshold: float) -> Sequence[np.ndarray]:
    balls = [data]
    while True:
        before = len(balls)
        balls = module.splits(balls, purity=threshold, splitting_method="k-means")
        if len(balls) == before:
            return balls


def _adaptive(module, data: np.ndarray, seed: int) -> Sequence[np.ndarray]:
    random.seed(seed)
    module.random.seed(seed)
    initial_purity = module.get_label_and_purity(data)[1]
    center = data[random.randrange(len(data))]
    distances = [module.calculate_distances(row[1:], center[1:]) for row in data]
    key = "_".join(str(float(value)) for value in center)
    result = module.splits(initial_purity, {key: [data, distances]})
    return [value[0] for value in result.values()]


def run(config: Mapping[str, Any]) -> Dict[str, Any]:
    seed = int(config["seed"])
    parameters = config.get("dataset_generation_parameters", {})
    X, y = make_moons(
        n_samples=int(parameters.get("n_samples", 300)),
        noise=float(parameters.get("noise", 0.12)), random_state=seed,
    )
    data = np.column_stack([y, X]).astype(float)
    upstream = (ROOT / str(config["upstream_path"])).resolve()
    _verify_commit(upstream, str(config["upstream_commit"]))
    module = _load_module(upstream, f"upstream_gbc_{config['variant']}")
    if config["variant"] == "original":
        balls = _original(module, data, float(config.get("hyperparameters", {}).get("purity", 0.85)))
    elif config["variant"] == "adaptive":
        balls = _adaptive(module, data, seed)
    else:
        raise ValueError(f"unknown variant: {config['variant']}")
    purities = [_purity(ball) for ball in balls]
    return {
        "metrics": {
            "accuracy": _resubstitution_accuracy(balls, data),
            "macro_f1": None, "auroc": None, "calibration_error": None,
            "additional": {"mean_ball_purity": float(np.mean(purities)), "evaluation": "resubstitution-only"},
        },
        "structure": {
            "granule_count": len(balls),
            "average_granule_size": float(np.mean([len(ball) for ball in balls])),
            "uncertain_sample_ratio": float(
                sum(len(ball) for ball, purity in zip(balls, purities) if purity < 0.85) / len(data)
            ),
            "additional": {"ball_sizes": [len(ball) for ball in balls], "ball_purities": purities},
        },
        "outcome": "success",
        "notes": "Author-code structure smoke test on generated moons; not a paper-table reproduction.",
    }

