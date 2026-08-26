"""Evaluate full-data exact GBABS samples with the frozen LightGBM protocol."""

from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
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


def load_closed_set(data_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_train, y_train = read_vectorized_features(data_dir, "train")
    x_test, y_test = read_vectorized_features(data_dir, "test")
    counts = Counter(y_train[y_train >= 0])
    eligible = np.array(sorted(label for label, count in counts.items() if count >= 10), dtype=np.int32)
    return x_train[np.isin(y_train, eligible)], y_train[np.isin(y_train, eligible)], x_test[np.isin(y_test, eligible)], y_test[np.isin(y_test, eligible)]


def model(seed: int) -> LGBMClassifier:
    return LGBMClassifier(objective="multiclass", n_estimators=300, learning_rate=0.1, num_leaves=31, subsample=1.0, colsample_bytree=1.0, n_jobs=-1, verbosity=-1, random_state=seed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--sample-ids", type=Path, required=True)
    parser.add_argument("--sampling-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-class-output", type=Path, required=True)
    args = parser.parse_args()
    x_train, y_train, x_test, y_test = load_closed_set(args.data_dir)
    selected = np.load(args.sample_ids)
    sampling = json.loads(args.sampling_summary.read_text(encoding="utf-8"))
    if np.any(selected < 0) or np.any(selected >= len(y_train)):
        raise ValueError("sample IDs are not valid closed-set training positions")
    x_fit, y_fit = x_train[selected], y_train[selected]
    rows: list[dict[str, object]] = []
    per_class_rows: list[dict[str, object]] = []
    labels = np.unique(y_test)
    for seed in range(5):
        with PeakMemory() as memory:
            clf = model(seed)
            started = time.perf_counter()
            clf.fit(x_fit, y_fit)
            fit_seconds = time.perf_counter() - started
            started = time.perf_counter()
            prediction = clf.predict(x_test)
            probabilities = clf.predict_proba(x_test)
            prediction_seconds = time.perf_counter() - started
        precision, recall, f1, support = precision_recall_fscore_support(y_test, prediction, labels=labels, zero_division=0)
        rows.append({
            "dataset": args.dataset, "source_dataset": "EMBER2024", "method": "GBABS_Exact", "seed": seed,
            "macro_f1": f1_score(y_test, prediction, labels=labels, average="macro", zero_division=0),
            "macro_recall": recall_score(y_test, prediction, labels=labels, average="macro", zero_division=0),
            "balanced_accuracy": balanced_accuracy_score(y_test, prediction),
            "weighted_f1": f1_score(y_test, prediction, labels=labels, average="weighted", zero_division=0),
            "accuracy": accuracy_score(y_test, prediction), "log_loss": log_loss(y_test, probabilities, labels=clf.classes_),
            "original_train_samples": len(y_train), "retained_train_samples": len(y_fit), "retention_ratio": len(y_fit) / len(y_train),
            "sampling_seconds": sampling["sampling_seconds"], "classifier_fit_seconds": fit_seconds,
            "end_to_end_fit_seconds": sampling["sampling_seconds"] + fit_seconds, "prediction_seconds": prediction_seconds,
            "peak_memory_bytes": max(memory.peak, sampling["peak_memory_bytes"]), "number_of_balls": sampling["number_of_balls"],
            "sampling_reused_across_seeds": True, "eligible_train_classes": len(np.unique(y_train)), "scored_test_classes": len(labels),
        })
        per_class_rows.extend({"dataset": args.dataset, "source_dataset": "EMBER2024", "method": "GBABS_Exact", "seed": seed, "family_id": int(label), "train_support": int((y_train == label).sum()), "test_support": int(count), "precision": float(p), "recall": float(r), "f1": float(score)} for label, p, r, score, count in zip(labels, precision, recall, f1, support, strict=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(args.output, index=False)
    pd.DataFrame(per_class_rows).to_parquet(args.per_class_output, index=False)
    print(pd.DataFrame(rows).to_json(orient="records"), flush=True)


if __name__ == "__main__":
    main()
