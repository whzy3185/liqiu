"""Cheap purity-cut structural probe; intentionally contains no membership attack."""

from __future__ import annotations

import numpy as np

from studies.risk_granularity.tree import GranulationTree


PROBE_THRESHOLDS = (0.70, 0.85, 0.90, 0.95, 0.99)


def probe_granular_structure(x: np.ndarray, y: np.ndarray, seed: int = 17) -> list[dict[str, object]]:
    tree = GranulationTree(random_state=seed, split_method="kmeans").fit(x, y)
    rows = []
    first_ball_count = None
    for threshold in PROBE_THRESHOLDS:
        balls = tree.cut(threshold)
        sizes = np.asarray([len(ball.indices) for ball in balls])
        radii = np.asarray([ball.radius for ball in balls])
        purity = np.asarray([ball.purity for ball in balls])
        if first_ball_count is None:
            first_ball_count = len(balls)
        rows.append({
            "threshold": threshold,
            "number_of_balls": len(balls),
            "mean_ball_size": float(sizes.mean()),
            "median_ball_size": float(np.median(sizes)),
            "min_ball_size": int(sizes.min()),
            "singleton_count": int((sizes == 1).sum()),
            "fraction_size_le_2": float((sizes <= 2).mean()),
            "fraction_size_le_5": float((sizes <= 5).mean()),
            "radius_mean": float(radii.mean()),
            "radius_median": float(np.median(radii)),
            "radius_dispersion": float(radii.std() / radii.mean()) if radii.mean() else 0.0,
            "purity_mean": float(purity.mean()),
            "purity_median": float(np.median(purity)),
            "purity_q25": float(np.quantile(purity, .25)),
            "purity_q75": float(np.quantile(purity, .75)),
        })
    for row in rows:
        row["fragmentation_ratio_95_70"] = next(item["number_of_balls"] for item in rows if item["threshold"] == .95) / first_ball_count
        row["fragmentation_ratio_99_70"] = next(item["number_of_balls"] for item in rows if item["threshold"] == .99) / first_ball_count
    return rows
