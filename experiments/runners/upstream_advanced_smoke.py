"""Paper-path smoke adapters for GBRS, GBFRS, and S3WD author code."""

from __future__ import annotations

import importlib.util
import builtins
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np
from sklearn.datasets import make_classification, make_moons
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler


ROOT = Path(__file__).resolve().parents[2]


def _verify(path: Path, commit: str) -> None:
    repo = path if path.is_dir() else path.parent
    while repo != repo.parent and not (repo / ".git").exists(): repo = repo.parent
    actual = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.strip()
    if actual != commit: raise RuntimeError(f"upstream commit mismatch: {actual} != {commit}")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def _result(accuracy, macro_f1, count, sizes, purities, uncertain, notes, additional=None):
    return {
        "metrics": {"accuracy": accuracy, "macro_f1": macro_f1, "auroc": None,
                    "calibration_error": None, "additional": additional or {}},
        "structure": {"granule_count": count,
                      "average_granule_size": float(np.mean(sizes)) if sizes else None,
                      "uncertain_sample_ratio": uncertain,
                      "additional": {"ball_sizes": sizes, "ball_purities": purities}},
        "outcome": "success", "notes": notes,
    }


def _gbrs(config, path, seed):
    module = _load(path, "upstream_gbrs")
    X, y = make_classification(n_samples=240, n_features=6, n_informative=3, n_redundant=1,
                               class_sep=1.0, flip_y=0.05, random_state=seed)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3, stratify=y, random_state=seed)
    scaler = MinMaxScaler(); X_train = scaler.fit_transform(X_train); X_test = scaler.transform(X_test)
    indexed = np.column_stack([X_train, y_train, np.arange(len(y_train))])
    selected = module.attribute_reduce(indexed, pur=1, d2=2)
    if not selected: raise RuntimeError("GBRS returned an empty reduction")
    classifier = KNeighborsClassifier(n_neighbors=5).fit(X_train[:, selected], y_train)
    predicted = classifier.predict(X_test[:, selected])
    balls = module.GBList(indexed, selected); balls.init_granular_balls(purity=1, min_sample=8)
    sizes, purities = balls.get_data_size(), balls.get_purity()
    return _result(float(accuracy_score(y_test, predicted)), float(f1_score(y_test, predicted, average="macro")),
                   len(sizes), sizes, purities, float(sum(s for s,p in zip(sizes,purities) if p < 1)/sum(sizes)),
                   "Author GBRS attribute-reduction path plus documented 5-NN downstream; synthetic smoke, not paper reproduction.",
                   {"selected_features": selected, "selected_count": len(selected)})


def _install_gbfrs_compatibility_shims():
    gui = types.ModuleType("PySimpleGUI"); gui.one_line_progress_meter = lambda *args, **kwargs: True
    sys.modules.setdefault("PySimpleGUI", gui)
    distutils = types.ModuleType("numpy.distutils"); fcompiler = types.ModuleType("numpy.distutils.fcompiler")
    fcompiler.none = None; distutils.fcompiler = fcompiler
    sys.modules.setdefault("numpy.distutils", distutils); sys.modules.setdefault("numpy.distutils.fcompiler", fcompiler)


def _gbfrs(config, path, seed):
    _install_gbfrs_compatibility_shims(); sys.path.insert(0, str(path.parent))
    try: module = _load(path, "upstream_gbfrs")
    finally: sys.path.pop(0)
    # Upstream's `from numpy import *` shadows built-in max, turning max(x, 1)
    # into numpy.max(x, axis=1). Restore the intended scalar operation without
    # editing or vendoring upstream source.
    sys.modules["BasicFunction.InformationGranular"].max = builtins.max
    X, y = make_classification(n_samples=180, n_features=6, n_informative=3, n_redundant=1,
                               class_sep=1.0, flip_y=0.04, random_state=seed)
    second_label = (X[:, 0] + X[:, 1] > np.median(X[:, 0] + X[:, 1])).astype(int)
    Y = np.column_stack([y, second_label]); Y[Y.sum(axis=1) == 0, 0] = 1
    indices = np.arange(len(y)); train, test = train_test_split(indices, test_size=.3, stratify=y, random_state=seed)
    scaler = StandardScaler(); X_train = scaler.fit_transform(X[train]); X_test = scaler.transform(X[test])
    ranking, upstream_seconds = module.AttributeReduction(
        X_train, Y[train], min_sample=12, miss_class_threshold=.5, distance_metric="euclidean", dataset_name="synthetic-smoke")
    ranking_zero = [int(value) - 1 for value in ranking]
    selected_count = min(4, len(ranking_zero)); selected = ranking_zero[:selected_count]
    classifier = KNeighborsClassifier(n_neighbors=5).fit(X_train[:, selected], y[train])
    predicted = classifier.predict(X_test[:, selected])
    return _result(float(accuracy_score(y[test], predicted)), float(f1_score(y[test], predicted, average="macro")),
                   None, [], [], None,
                   "MIT GBFRS full AttributeReduction path with no-op GUI, removed-distutils, and shadowed built-in max compatibility shims; synthetic smoke.",
                   {"feature_ranking_zero_based": ranking_zero, "selected_features": selected,
                    "upstream_reported_seconds": float(upstream_seconds)})


def _s3wd(config, path, seed):
    code = path; gb_module = _load(code / "GBNRS3WDGBs.py", "upstream_s3wd_gb")
    tool = _load(code / "tool.py", "upstream_s3wd_tool"); predictor = _load(code / "tools.py", "upstream_s3wd_predictor")
    X, y = make_moons(n_samples=360, noise=.18, random_state=seed)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3, stratify=y, random_state=seed)
    scaler = MinMaxScaler(); X_train = scaler.fit_transform(X_train); X_test = scaler.transform(X_test)
    balls = gb_module.GBList(np.column_stack([X_train, y_train])); balls.init_granular_balls()
    membership = tool.get_membership_table(balls); beta, alpha, mismatch = tool.compute_best_beta(balls, membership)
    predicted = np.array([predictor.GBKNN3WD_compute_label(row, balls, beta, alpha) for row in X_test])
    covered = predicted != -1; coverage = float(np.mean(covered))
    selective_accuracy = float(accuracy_score(y_test[covered], predicted[covered])) if covered.any() else None
    selective_f1 = float(f1_score(y_test[covered], predicted[covered], average="macro")) if covered.any() else None
    overall = float(np.mean(predicted == y_test))
    sizes, purities = balls.get_data_size(), balls.get_purity()
    return _result(overall, selective_f1, len(sizes), sizes, purities, 1.0 - coverage,
                   "Author S3WD threshold and three-way prediction path; accuracy counts defer as incorrect, selective metrics are separate.",
                   {"coverage": coverage, "selective_accuracy": selective_accuracy,
                    "beta": float(beta), "alpha": float(alpha), "fuzziness_mismatch": float(mismatch)})


def run(config: Mapping[str, Any]) -> Dict[str, Any]:
    seed = int(config["seed"]); np.random.seed(seed)
    path = (ROOT / str(config["upstream_path"])).resolve(); _verify(path, str(config["upstream_commit"]))
    variant = config["variant"]
    if variant == "gbrs": return _gbrs(config, path, seed)
    if variant == "gbfrs": return _gbfrs(config, path, seed)
    if variant == "s3wd_gbrs": return _s3wd(config, path, seed)
    raise ValueError(f"unknown variant: {variant}")
