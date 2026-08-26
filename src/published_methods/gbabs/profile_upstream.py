"""Measure the pinned upstream GBABS implementation without altering its logic."""

from __future__ import annotations

import argparse
import resource
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from thrember import read_vectorized_features


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-dir", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--rho", type=int, default=5)
    args = parser.parse_args()
    sys.path.insert(0, str(args.upstream_dir))
    import GBABS  # noqa: PLC0415
    import RD_GBG  # noqa: PLC0415

    x, y = read_vectorized_features(args.data_dir, "train")
    chosen = np.flatnonzero(y >= 0)[: args.rows]
    x, y = x[chosen], y[chosen]
    data = np.column_stack((y, MinMaxScaler().fit_transform(x), np.arange(len(y))))
    original = RD_GBG.generateGBList
    observed: dict[str, int] = {}

    def counting_generate(data_arg: np.ndarray, k: int):
        balls, centers = original(data_arg, k)
        observed["balls"] = len(balls)
        return balls, centers

    RD_GBG.generateGBList = counting_generate
    np.random.seed(args.seed)
    cpu_before = time.process_time()
    wall_before = time.perf_counter()
    sampled = GBABS.GBABS(data, args.rho).bound_sampling()
    wall = time.perf_counter() - wall_before
    cpu = time.process_time() - cpu_before
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(
        ",".join(
            map(
                str,
                (
                    args.rows,
                    x.shape[1],
                    args.rho,
                    args.seed,
                    observed["balls"],
                    len(sampled),
                    f"{wall:.9f}",
                    f"{cpu:.9f}",
                    usage.ru_maxrss,
                ),
            )
        )
    )


if __name__ == "__main__":
    main()
