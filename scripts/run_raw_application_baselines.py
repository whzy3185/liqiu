"""Run fixed-budget conventional baselines on prepared industrial datasets."""
from __future__ import annotations

import hashlib
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
from applications.models import capped_fit_indices, conventional_models


OUTPUT = ROOT / "results" / "application_scout" / "raw_baselines.parquet"
MANIFEST = ROOT / "results" / "application_scout" / "raw_baselines_manifest.json"
FAILURES = ROOT / "results" / "application_scout" / "failures.jsonl"
DATASETS = ("steel_plates", "secom", "aps_failure")
SEEDS = (1, 7, 21, 42, 2026)


def main() -> int:
    rows: list[dict] = []
    split_summaries: dict[str, dict] = {}
    for dataset_name in DATASETS:
        for seed in SEEDS:
            split = load_industrial_split(
                dataset_name, seed, ROOT / "data" / "industrial_fault" / "cache" / "openml"
            )
            imputer = SimpleImputer(strategy="median", keep_empty_features=True).fit(split.X_train)
            X_train = imputer.transform(split.X_train)
            X_validation = imputer.transform(split.X_validation)
            X_test = imputer.transform(split.X_test)
            scaler = StandardScaler().fit(X_train)
            X_train = scaler.transform(X_train)
            X_validation = scaler.transform(X_validation)
            X_test = scaler.transform(X_test)
            n_classes = len(np.unique(np.concatenate([split.y_train, split.y_validation, split.y_test])))
            split_summaries[f"{dataset_name}:s{seed}"] = {
                "source": split.source,
                "protocol": split.split_protocol,
                "train": len(split.y_train),
                "validation": len(split.y_validation),
                "test": len(split.y_test),
                "features": X_train.shape[1],
                "test_class_counts": {
                    str(label): int((split.y_test == label).sum()) for label in np.unique(split.y_test)
                },
            }
            class_counts = {
                int(label): int((split.y_train == label).sum()) for label in np.unique(split.y_train)
            }
            for spec in conventional_models(seed, n_classes, class_counts=class_counts):
                fit_indices = capped_fit_indices(split.y_train, spec.fit_cap, seed)
                try:
                    started = time.perf_counter()
                    spec.estimator.fit(X_train[fit_indices], split.y_train[fit_indices])
                    fit_seconds = time.perf_counter() - started
                    started = time.perf_counter()
                    prediction = np.asarray(spec.estimator.predict(X_test)).reshape(-1)
                    predict_seconds = time.perf_counter() - started
                    rows.append({
                        "experiment": "raw_baseline_v1",
                        "domain": "industrial_tabular",
                        "dataset": dataset_name,
                        "seed": seed,
                        "model": spec.name,
                        "variant": "raw",
                        "fit_samples": len(fit_indices),
                        "train_samples": len(split.y_train),
                        "test_samples": len(split.y_test),
                        "n_features": X_train.shape[1],
                        "fit_seconds": fit_seconds,
                        "predict_seconds": predict_seconds,
                        "split_protocol": split.split_protocol,
                        **industrial_metrics(split.y_test, prediction),
                    })
                    print(dataset_name, seed, spec.name, f"F1={rows[-1]['macro_f1']:.4f}", flush=True)
                except Exception as exc:
                    FAILURES.parent.mkdir(parents=True, exist_ok=True)
                    with FAILURES.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps({
                            "experiment": "raw_baseline_v1",
                            "dataset": dataset_name,
                            "seed": seed,
                            "model": spec.name,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "traceback": traceback.format_exc(),
                        }, sort_keys=True) + "\n")
                    print(dataset_name, seed, spec.name, "FAILURE", type(exc).__name__, flush=True)
    frame = pd.DataFrame(rows).sort_values(["dataset", "seed", "model"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(OUTPUT, index=False)
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    MANIFEST.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": digest,
                "rows": len(frame),
                "datasets": split_summaries,
                "notes": (
                    "Tree/boosting models use all training rows. KNN and RBF-SVM are diagnostic "
                    "and use a stratified cap of 5000 rows when the dataset is larger. No model "
                    "or threshold is selected from test performance."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(frame)} rows to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
