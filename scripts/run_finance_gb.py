"""Prompt-15 finance Cheap Test: Raw, GBFeat, and GB reliability weighting."""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from applications.finance_metrics import choose_validation_threshold, finance_metrics
from applications.finance_tabular import load_finance_split
from applications.models import conventional_models
from gb_application import cross_fitted_gb_features
from gb_application.models import append_gb_features


OUTPUT = ROOT / "results" / "application_scout" / "finance_gb.csv"
AUDIT = ROOT / "results" / "application_scout" / "finance_gb_audit.json"
FAILURES = ROOT / "results" / "application_scout" / "failures.jsonl"
DATASETS = ("taiwan_default", "australian_credit", "polish_bankruptcy_5year")
SEEDS = (1, 7, 21, 42, 2026)
MODELS = {"xgboost", "lightgbm", "catboost"}


def _preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    categorical = list(X.select_dtypes(include=["object", "category", "bool"]).columns)
    numeric = [column for column in X.columns if column not in categorical]
    return ColumnTransformer(
        [
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median", keep_empty_features=True))]), numeric),
            (
                "categorical",
                Pipeline([
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ]),
                categorical,
            ),
        ],
        sparse_threshold=0.0,
    )


def main() -> int:
    rows: list[dict] = []
    audits: dict[str, dict] = {}
    for dataset_name in DATASETS:
        for seed in SEEDS:
            key = f"{dataset_name}:s{seed}"
            try:
                split = load_finance_split(dataset_name, seed)
                transform = _preprocessor(split.X_train).fit(split.X_train)
                X_train = transform.transform(split.X_train)
                X_validation = transform.transform(split.X_validation)
                X_test = transform.transform(split.X_test)
                scaler = StandardScaler().fit(X_train)
                X_train = scaler.transform(X_train)
                X_validation = scaler.transform(X_validation)
                X_test = scaler.transform(X_test)
                crossfit_started = time.perf_counter()
                crossfit = cross_fitted_gb_features(
                    X_train,
                    split.y_train,
                    X_validation,
                    X_test,
                    seed=seed,
                    purity=0.9,
                    min_samples=5,
                    max_balls=256,
                    generator_fit_cap=12_000 if len(X_train) > 12_000 else None,
                )
                gb_seconds = time.perf_counter() - crossfit_started
                matrices = {
                    "raw": (X_train, X_validation, X_test, None),
                    "gbfeat": (
                        append_gb_features(X_train, crossfit.train),
                        append_gb_features(X_validation, crossfit.validation),
                        append_gb_features(X_test, crossfit.test),
                        None,
                    ),
                    # OOF purity is the predeclared W1 reliability score.
                    "gbweight": (X_train, X_validation, X_test, np.clip(crossfit.train[:, 4], 0.05, 1.0)),
                }
                class_counts = {int(label): int((split.y_train == label).sum()) for label in np.unique(split.y_train)}
                audits[key] = {
                    "full_fit_count": crossfit.full_fit_count,
                    "n_balls": len(crossfit.full_generator.balls_),
                    "oof_disjoint": all(not (set(a.fit_indices) & set(a.query_indices)) for a in crossfit.audits),
                }
                for variant, (train, validation, test, sample_weight) in matrices.items():
                    for spec in conventional_models(seed, 2, class_counts=class_counts):
                        if spec.name not in MODELS:
                            continue
                        started = time.perf_counter()
                        fit_args = {"sample_weight": sample_weight} if sample_weight is not None else {}
                        spec.estimator.fit(train, split.y_train, **fit_args)
                        fit_seconds = time.perf_counter() - started
                        validation_probability = spec.estimator.predict_proba(validation)[:, 1]
                        threshold = choose_validation_threshold(split.y_validation, validation_probability)
                        started = time.perf_counter()
                        test_probability = spec.estimator.predict_proba(test)[:, 1]
                        predict_seconds = time.perf_counter() - started
                        rows.append({
                            "experiment": "finance_gb_v1",
                            "dataset": dataset_name,
                            "seed": seed,
                            "model": spec.name,
                            "variant": variant,
                            "train_samples": len(split.y_train),
                            "test_samples": len(split.y_test),
                            "n_features": train.shape[1],
                            "fit_seconds": fit_seconds,
                            "predict_seconds": predict_seconds,
                            "gb_feature_seconds": gb_seconds if variant != "raw" else 0.0,
                            "n_balls": len(crossfit.full_generator.balls_) if variant != "raw" else np.nan,
                            "split_protocol": split.split_protocol,
                            "validation_pr_auc": float(average_precision_score(split.y_validation, validation_probability)),
                            "validation_roc_auc": float(roc_auc_score(split.y_validation, validation_probability)),
                            **finance_metrics(split.y_test, test_probability, threshold),
                        })
                        print(dataset_name, seed, spec.name, variant, f"PR={rows[-1]['pr_auc']:.4f}", flush=True)
            except Exception as exc:
                with FAILURES.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        "experiment": "finance_gb_v1", "dataset": dataset_name, "seed": seed,
                        "error_type": type(exc).__name__, "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }, sort_keys=True) + "\n")
                print(key, "FAILURE", type(exc).__name__, str(exc), flush=True)
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "model", "variant"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False)
    AUDIT.write_text(json.dumps(audits, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", len(frame), "rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
