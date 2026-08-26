"""Prompt-8 Cheap Test: raw versus cross-fitted GB structural features."""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from applications.industrial_tabular import load_industrial_split
from applications.metrics import industrial_metrics
from applications.models import conventional_models
from gb_application import cross_fitted_gb_features
from gb_application.models import append_gb_features


RAW = ROOT / "results" / "application_scout" / "raw_baselines.parquet"
OUTPUT = ROOT / "results" / "application_scout" / "fault_gbfeat.csv"
AUDIT = ROOT / "results" / "application_scout" / "fault_gbfeat_audit.json"
FAILURES = ROOT / "results" / "application_scout" / "failures.jsonl"
DATASETS = ("steel_plates", "secom", "aps_failure")
SEEDS = (1, 7, 21, 42, 2026)
MODELS = {"xgboost", "lightgbm", "catboost", "random_forest", "extra_trees"}


def main() -> int:
    raw = pd.read_parquet(RAW)
    raw = raw[raw.model.isin(MODELS)].copy()
    raw["gb_feature_seconds"] = 0.0
    raw["n_balls"] = np.nan
    raw["average_ball_size"] = np.nan
    raw["compression_ratio"] = np.nan
    rows = raw.to_dict("records")
    audits: dict[str, dict] = {}
    for dataset_name in DATASETS:
        for seed in SEEDS:
            key = f"{dataset_name}:s{seed}"
            try:
                split = load_industrial_split(
                    dataset_name,
                    seed,
                    ROOT / "data" / "industrial_fault" / "cache" / "openml",
                )
                imputer = SimpleImputer(strategy="median", keep_empty_features=True).fit(split.X_train)
                X_train = imputer.transform(split.X_train)
                X_validation = imputer.transform(split.X_validation)
                X_test = imputer.transform(split.X_test)
                scaler = StandardScaler().fit(X_train)
                X_train = scaler.transform(X_train)
                X_validation = scaler.transform(X_validation)
                X_test = scaler.transform(X_test)
                started = time.perf_counter()
                crossfit = cross_fitted_gb_features(
                    X_train,
                    split.y_train,
                    X_validation,
                    X_test,
                    seed=seed,
                    purity=0.9,
                    min_samples=5,
                    max_balls=256,
                    generator_fit_cap=12_000 if dataset_name == "aps_failure" else None,
                )
                feature_seconds = time.perf_counter() - started
                augmented_train = append_gb_features(X_train, crossfit.train)
                augmented_test = append_gb_features(X_test, crossfit.test)
                n_balls = len(crossfit.full_generator.balls_)
                class_counts = {
                    int(label): int((split.y_train == label).sum())
                    for label in np.unique(split.y_train)
                }
                audits[key] = {
                    "generator_full_fit_count": crossfit.full_fit_count,
                    "n_balls": n_balls,
                    "folds": [
                        {
                            "fold": audit.fold,
                            "fit_count": len(audit.fit_indices),
                            "query_count": len(audit.query_indices),
                            "n_balls": audit.n_balls,
                            "disjoint": not bool(set(audit.fit_indices) & set(audit.query_indices)),
                        }
                        for audit in crossfit.audits
                    ],
                }
                n_classes = len(class_counts)
                for spec in conventional_models(seed, n_classes, class_counts=class_counts):
                    if spec.name not in MODELS:
                        continue
                    started = time.perf_counter()
                    spec.estimator.fit(augmented_train, split.y_train)
                    fit_seconds = time.perf_counter() - started
                    started = time.perf_counter()
                    prediction = np.asarray(spec.estimator.predict(augmented_test)).reshape(-1)
                    predict_seconds = time.perf_counter() - started
                    rows.append({
                        "experiment": "fault_gbfeat_v1",
                        "domain": "industrial_tabular",
                        "dataset": dataset_name,
                        "seed": seed,
                        "model": spec.name,
                        "variant": "gbfeat",
                        "fit_samples": len(split.y_train),
                        "train_samples": len(split.y_train),
                        "test_samples": len(split.y_test),
                        "n_features": augmented_train.shape[1],
                        "fit_seconds": fit_seconds,
                        "predict_seconds": predict_seconds,
                        "split_protocol": split.split_protocol,
                        "gb_feature_seconds": feature_seconds,
                        "n_balls": n_balls,
                        "average_ball_size": crossfit.full_fit_count / n_balls,
                        "compression_ratio": n_balls / crossfit.full_fit_count,
                        **industrial_metrics(split.y_test, prediction),
                    })
                    print(dataset_name, seed, spec.name, f"GB F1={rows[-1]['macro_f1']:.4f}", flush=True)
            except Exception as exc:
                with FAILURES.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        "experiment": "fault_gbfeat_v1",
                        "dataset": dataset_name,
                        "seed": seed,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }, sort_keys=True) + "\n")
                print(key, "FAILURE", type(exc).__name__, str(exc), flush=True)
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "model", "variant"])
    frame.to_csv(OUTPUT, index=False)
    AUDIT.write_text(json.dumps(audits, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", len(frame), "rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

