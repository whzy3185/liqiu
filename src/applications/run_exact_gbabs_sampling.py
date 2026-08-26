"""Run the exact verified GBABS representation on one EMBER2024 family task."""

from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter
from pathlib import Path

import numpy as np
import psutil
from sklearn.preprocessing import MinMaxScaler
from thrember import read_vectorized_features

from src.published_methods.gbabs_exact import ExactGBABS


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


def load_closed_set(data_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    x_train, y_train = read_vectorized_features(data_dir, "train")
    counts = Counter(y_train[y_train >= 0])
    eligible = np.array(sorted(label for label, count in counts.items() if count >= 10), dtype=np.int32)
    mask = np.isin(y_train, eligible)
    return x_train[mask], y_train[mask]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--ids-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    x, y = load_closed_set(args.data_dir)
    scaled = MinMaxScaler().fit_transform(x)
    with PeakMemory() as memory:
        started = time.perf_counter()
        result = ExactGBABS(scaled, y, np.arange(len(y), dtype=np.int64), rho=5).sample(seed=0)
        seconds = time.perf_counter() - started
    args.ids_output.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.ids_output, np.asarray(result.boundary_sample_indices, dtype=np.int64))
    summary = {
        "dataset": args.dataset,
        "original_train_samples": len(y),
        "features": x.shape[1],
        "rho": 5,
        "seed": 0,
        "number_of_balls": len(result.balls),
        "retained_train_samples": len(result.boundary_sample_indices),
        "retention_ratio": len(result.boundary_sample_indices) / len(y),
        "sampling_seconds": seconds,
        "peak_memory_bytes": memory.peak,
        "low_density_record_count": len(result.low_density_records),
        "outlier_record_count": len(result.outlier_records),
        "sample_id_file": str(args.ids_output),
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
