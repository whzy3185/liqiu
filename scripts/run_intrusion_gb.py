"""Prompt-16 high-bar diagnostic screen on accessible UNSW-NB15 export."""
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
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from applications.finance_metrics import choose_validation_threshold, finance_metrics
from applications.intrusion_tabular import load_unsw_nb15_screen
from applications.models import conventional_models
from gb_application import cross_fitted_gb_features
from gb_application.models import append_gb_features


OUTPUT = ROOT / "results" / "application_scout" / "intrusion_gb.csv"
AUDIT = ROOT / "results" / "application_scout" / "intrusion_gb_audit.json"
FAILURES = ROOT / "results" / "application_scout" / "failures.jsonl"
SEEDS = (1, 7, 21, 42, 2026)
MODELS = {"xgboost", "lightgbm", "catboost"}


def _preprocessor(X):
    categorical = list(X.select_dtypes(include=["object", "category", "bool"]).columns)
    numeric = [column for column in X.columns if column not in categorical]
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median", keep_empty_features=True))]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical),
    ], sparse_threshold=0.0)


def main() -> int:
    rows, audits = [], {}
    for seed in SEEDS:
        try:
            split = load_unsw_nb15_screen(seed, str(ROOT / "data" / "intrusion" / "cache" / "openml"))
            encoder = _preprocessor(split.X_train).fit(split.X_train)
            train, validation, test = [encoder.transform(frame) for frame in (split.X_train, split.X_validation, split.X_test)]
            scaler = StandardScaler().fit(train)
            train, validation, test = [scaler.transform(matrix) for matrix in (train, validation, test)]
            started = time.perf_counter()
            crossfit = cross_fitted_gb_features(
                train, split.y_train, validation, test, seed=seed, purity=0.9, min_samples=5,
                max_balls=256, generator_fit_cap=12_000,
            )
            feature_seconds = time.perf_counter() - started
            variants = {
                "raw": (train, validation, test, None),
                "gbfeat": (append_gb_features(train, crossfit.train), append_gb_features(validation, crossfit.validation), append_gb_features(test, crossfit.test), None),
                "gbweight": (train, validation, test, np.clip(crossfit.train[:, 4], 0.05, 1.0)),
            }
            counts = {int(label): int((split.y_train == label).sum()) for label in np.unique(split.y_train)}
            audits[f"unsw_nb15:s{seed}"] = {"oof_disjoint": all(not (set(a.fit_indices) & set(a.query_indices)) for a in crossfit.audits), "n_balls": len(crossfit.full_generator.balls_)}
            for variant, (X_train, X_val, X_test, sample_weight) in variants.items():
                for spec in conventional_models(seed, 2, class_counts=counts):
                    if spec.name not in MODELS:
                        continue
                    started = time.perf_counter()
                    spec.estimator.fit(X_train, split.y_train, **({"sample_weight": sample_weight} if sample_weight is not None else {}))
                    fit_seconds = time.perf_counter() - started
                    val_prob = spec.estimator.predict_proba(X_val)[:, 1]
                    threshold = choose_validation_threshold(split.y_validation, val_prob)
                    started = time.perf_counter()
                    test_prob = spec.estimator.predict_proba(X_test)[:, 1]
                    predict_seconds = time.perf_counter() - started
                    metric = finance_metrics(split.y_test, test_prob, threshold)
                    rows.append({
                        "experiment": "intrusion_gb_v1", "dataset": "unsw_nb15_openml_diagnostic", "seed": seed,
                        "model": spec.name, "variant": variant, "train_samples": len(split.y_train),
                        "test_samples": len(split.y_test), "n_features": X_train.shape[1],
                        "fit_seconds": fit_seconds, "predict_seconds": predict_seconds,
                        "gb_feature_seconds": feature_seconds if variant != "raw" else 0.0,
                        "n_balls": len(crossfit.full_generator.balls_) if variant != "raw" else np.nan,
                        "validation_pr_auc": float(average_precision_score(split.y_validation, val_prob)),
                        "split_protocol": split.protocol, **metric,
                    })
                    print(seed, spec.name, variant, f"PR={metric['pr_auc']:.4f}", flush=True)
        except Exception as exc:
            with FAILURES.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"experiment":"intrusion_gb_v1","seed":seed,"error_type":type(exc).__name__,"error":str(exc),"traceback":traceback.format_exc()}, sort_keys=True)+"\n")
            print(seed, "FAILURE", type(exc).__name__, str(exc), flush=True)
    pd.DataFrame(rows).sort_values(["seed","model","variant"]).to_csv(OUTPUT, index=False)
    AUDIT.write_text(json.dumps(audits, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("wrote",len(rows),"rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

