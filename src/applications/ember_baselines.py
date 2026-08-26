"""Frozen Raw/ClassWeight/RUS LightGBM baselines for EMBER2024 family tasks."""

from __future__ import annotations

import argparse
import threading
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
from imblearn.under_sampling import RandomUnderSampler
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss, precision_recall_fscore_support, recall_score
from thrember import read_vectorized_features


class PeakMemory:
    def __init__(self) -> None:
        self.process = psutil.Process()
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.sample, daemon=True)

    def sample(self) -> None:
        while not self.stop.wait(0.05):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self) -> "PeakMemory":
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop.set()
        self.thread.join()


def load_closed_set(root: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_train, y_train = read_vectorized_features(root, subset="train")
    x_test, y_test = read_vectorized_features(root, subset="test")
    counts = Counter(y_train[y_train >= 0])
    eligible = np.array(sorted(label for label, count in counts.items() if count >= 10), dtype=np.int32)
    return x_train[np.isin(y_train, eligible)], y_train[np.isin(y_train, eligible)], x_test[np.isin(y_test, eligible)], y_test[np.isin(y_test, eligible)]


def make_model(seed: int, class_weight: str | None = None) -> LGBMClassifier:
    return LGBMClassifier(objective="multiclass", n_estimators=300, learning_rate=0.1, num_leaves=31, subsample=1.0, colsample_bytree=1.0, n_jobs=-1, verbosity=-1, random_state=seed, class_weight=class_weight)


def run_one(dataset: str, method: str, seed: int, root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    x_train, y_train, x_test, y_test = load_closed_set(root)
    original_rows = len(y_train)
    sampling_seconds = 0.0
    x_fit, y_fit, weight = x_train, y_train, None
    if method == "ClassWeight":
        weight = "balanced"
    elif method == "RandomUnderSampling":
        start = time.perf_counter()
        x_fit, y_fit = RandomUnderSampler(random_state=seed, sampling_strategy="auto").fit_resample(x_train, y_train)
        sampling_seconds = time.perf_counter() - start
    with PeakMemory() as memory:
        model = make_model(seed, class_weight=weight)
        start = time.perf_counter()
        model.fit(x_fit, y_fit)
        fit_seconds = time.perf_counter() - start
        start = time.perf_counter()
        y_pred = model.predict(x_test)
        probabilities = model.predict_proba(x_test)
        prediction_seconds = time.perf_counter() - start
    labels = np.unique(y_test)
    precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred, labels=labels, zero_division=0)
    result = {
        "dataset": dataset, "source_dataset": "EMBER2024", "method": method, "seed": seed,
        "macro_f1": f1_score(y_test, y_pred, labels=labels, average="macro", zero_division=0),
        "macro_recall": recall_score(y_test, y_pred, labels=labels, average="macro", zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
        "weighted_f1": f1_score(y_test, y_pred, labels=labels, average="weighted", zero_division=0),
        "accuracy": accuracy_score(y_test, y_pred), "log_loss": log_loss(y_test, probabilities, labels=model.classes_),
        "original_train_samples": original_rows, "retained_train_samples": len(y_fit), "retention_ratio": len(y_fit) / original_rows,
        "sampling_seconds": sampling_seconds, "classifier_fit_seconds": fit_seconds,
        "end_to_end_fit_seconds": sampling_seconds + fit_seconds, "prediction_seconds": prediction_seconds,
        "peak_memory_bytes": memory.peak, "eligible_train_classes": len(np.unique(y_train)), "scored_test_classes": len(labels),
    }
    per_class = [
        {"dataset": dataset, "source_dataset": "EMBER2024", "method": method, "seed": seed, "family_id": int(label), "train_support": int((y_train == label).sum()), "test_support": int(s), "precision": float(p), "recall": float(r), "f1": float(score)}
        for label, p, r, score, s in zip(labels, precision, recall, f1, support, strict=True)
    ]
    return result, per_class


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-class-output", type=Path, required=True)
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    per_class_rows: list[dict[str, object]] = []
    for dataset, subdir in (("EMBER2024_ELF", "elf"), ("EMBER2024_PDF", "pdf")):
        for method in ("Raw", "ClassWeight", "RandomUnderSampling"):
            for seed in range(5):
                print(f"START dataset={dataset} method={method} seed={seed}", flush=True)
                result, class_rows = run_one(dataset, method, seed, args.data_root / subdir)
                print(f"DONE {result}", flush=True)
                rows.append(result)
                per_class_rows.extend(class_rows)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                pd.DataFrame(rows).to_parquet(args.output, index=False)
                pd.DataFrame(per_class_rows).to_parquet(args.per_class_output, index=False)


if __name__ == "__main__":
    main()
