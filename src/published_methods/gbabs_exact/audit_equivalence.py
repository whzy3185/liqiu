"""Compare pinned upstream GBABS with the index-backed exact implementation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from thrember import read_vectorized_features

from .core import ExactGBABS


def run_audit(upstream_dir: Path, data_dir: Path, rows: int, seed: int = 0, rho: int = 5) -> dict[str, object]:
    sys.path.insert(0, str(upstream_dir))
    import GBABS  # noqa: PLC0415
    import RD_GBG  # noqa: PLC0415

    x, y = read_vectorized_features(data_dir, "train")
    source_rows = np.flatnonzero(y >= 0)[:rows]
    x, y = x[source_rows], y[source_rows]
    x = MinMaxScaler().fit_transform(x)
    sample_ids = np.arange(len(y), dtype=np.int64)
    data = np.column_stack((y, x, sample_ids))
    observed: dict[str, object] = {"balls": [], "outliers": [], "low_density": []}
    original_generate = RD_GBG.generateGBList
    original_detect = RD_GBG.GranularBallManager.detect_outliers
    original_generate_balls = RD_GBG.GranularBallManager.generate_granular_balls

    def capture_generate(data_arg: np.ndarray, k: int):
        balls, centers = original_generate(data_arg, k)
        observed["balls"] = balls
        return balls, centers

    def capture_detect(manager, data_dis_sort, k, center_label):
        result = original_detect(manager, data_dis_sort, k, center_label)
        observed["outliers"].append((int(data_dis_sort[0, -2]), int(result)))
        return result

    def capture_generate_balls(manager, balls, low_density, data_arg, k):
        result = original_generate_balls(manager, balls, low_density, data_arg, k)
        observed["low_density"] = [(int(index), int(status)) for index, status in low_density]
        return result

    RD_GBG.generateGBList = capture_generate
    RD_GBG.GranularBallManager.detect_outliers = capture_detect
    RD_GBG.GranularBallManager.generate_granular_balls = capture_generate_balls
    try:
        np.random.seed(seed)
        upstream = GBABS.GBABS(data, rho)
        upstream.bound_sampling()
    finally:
        RD_GBG.generateGBList = original_generate
        RD_GBG.GranularBallManager.detect_outliers = original_detect
        RD_GBG.GranularBallManager.generate_granular_balls = original_generate_balls
    np.random.seed(seed)
    exact = ExactGBABS(x, y, sample_ids, rho).sample()
    upstream_balls = observed["balls"]
    membership = all(np.array_equal(ball.data[:, -1].astype(np.int64), candidate.member_indices) for ball, candidate in zip(upstream_balls, exact.balls, strict=True))
    labels = len(upstream_balls) == len(exact.balls) and all(ball.label == candidate.label for ball, candidate in zip(upstream_balls, exact.balls, strict=True))
    centers = len(upstream_balls) == len(exact.balls) and all(np.allclose(ball.center, candidate.center) for ball, candidate in zip(upstream_balls, exact.balls, strict=True))
    radii = len(upstream_balls) == len(exact.balls) and all(np.allclose(ball.radius, candidate.radius) for ball, candidate in zip(upstream_balls, exact.balls, strict=True))
    upstream_boundary = tuple(int(index) for index in upstream.boundary_sample_indices)
    boundary = upstream_boundary == exact.boundary_sample_indices
    low_density = tuple(observed["low_density"]) == exact.low_density_records
    outliers = tuple(observed["outliers"]) == exact.outlier_records
    passed = all((membership, labels, centers, radii, boundary, low_density, outliers))
    return {"rows": rows, "features": x.shape[1], "rho": rho, "seed": seed, "official_balls": len(upstream_balls), "exact_balls": len(exact.balls), "membership_exact": membership, "labels_exact": labels, "centers_allclose": centers, "radii_allclose": radii, "boundary_order_exact": boundary, "low_density_exact": low_density, "outliers_exact": outliers, "result": "EXACT_EQUIVALENCE_PASS" if passed else "FAIL"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-dir", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--rows", type=int, required=True)
    args = parser.parse_args()
    result = run_audit(args.upstream_dir, args.data_dir, args.rows)
    print(",".join(str(result[key]) for key in result))


if __name__ == "__main__":
    main()
