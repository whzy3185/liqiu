"""Small-ball and boundary mechanism audit for the frozen A3 confirmation set."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from studies.privacy_refinement.a3 import attack_metrics, gb_release, kmeans_release, split_standardize, synthetic_regime
from studies.risk_granularity.tree import GranulationTree


CONFIRMATION_POINTS = (
    {"dimension": 60, "redundant_fraction": 0.0, "label_noise": 0.05},
    {"dimension": 60, "redundant_fraction": 0.1, "label_noise": 0.15},
    {"dimension": 100, "redundant_fraction": 0.0, "label_noise": 0.05},
    {"dimension": 100, "redundant_fraction": 0.1, "label_noise": 0.15},
)
SEEDS = (2, 13, 73, 314, 808)
FINE_THRESHOLDS = (0.90, 0.95, 0.99)


def size_bin(size: int) -> str:
    if size <= 2:
        return "1-2"
    if size <= 5:
        return "3-5"
    if size <= 10:
        return "6-10"
    if size <= 20:
        return "11-20"
    return ">20"


def candidate_rows() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for point in CONFIRMATION_POINTS:
        for seed in SEEDS:
            params = {"n": 600, "separation": 2.0, "density_ratio": 5.0, "minority_fraction": 0.30, "modes": 3, **point}
            dataset = f"confirm_d{params['dimension']}_redundant{params['redundant_fraction']:g}_noise{params['label_noise']:g}"
            x, y = synthetic_regime(seed=seed, **params)
            x_member, y_member, x_nonmember, _ = split_standardize(x, y, seed)
            tree = GranulationTree(random_state=211 + seed, split_method="kmeans").fit(x_member, y_member)
            query = np.vstack([x_member, x_nonmember])
            member = np.r_[np.ones(len(x_member), dtype=int), np.zeros(len(x_nonmember), dtype=int)]
            for threshold in FINE_THRESHOLDS:
                gb = gb_release(tree, x_member, threshold, "release_3")
                km = kmeans_release(x_member, y_member, len(gb.members), seed, "release_3")
                for release in (gb, km):
                    _, score, nearest = attack_metrics(release, x_member, x_nonmember, seed, "logistic")
                    distances = np.linalg.norm(query - release.centers[nearest], axis=1)
                    radii = release.radii[nearest]
                    normalized = np.divide(distances, radii, out=np.full(len(query), np.nan), where=radii > 1e-12)
                    for index in range(len(query)):
                        ball = int(nearest[index])
                        rows.append({
                            "dataset": dataset, "seed": seed, "threshold": threshold, "method": release.method,
                            "member": int(member[index]), "attack_score": float(score[index]), "nearest_ball": ball,
                            "ball_size": int(release.sizes[ball]), "ball_size_bin": size_bin(int(release.sizes[ball])),
                            "purity": float(release.purities[ball]), "radius": float(release.radii[ball]),
                            "refinement_depth": int(release.depths[ball]), "normalized_distance": float(normalized[index]),
                            **point,
                        })
    return pd.DataFrame(rows)


def subgroup_metrics(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["dataset", "seed", "threshold", "method", "ball_size_bin"]
    for key, group in candidates.groupby(keys):
        if group.member.nunique() < 2:
            auc = float("nan")
        else:
            auc = float(roc_auc_score(group.member, group.attack_score))
        rows.append(dict(zip(keys, key), sample_count=len(group), member_count=int(group.member.sum()), roc_auc=auc))
    return pd.DataFrame(rows)


def regressions(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    names = ["log_ball_size", "purity", "radius", "refinement_depth", "normalized_distance"]
    for method, group in candidates.groupby("method"):
        data = group.replace([np.inf, -np.inf], np.nan).dropna(subset=["ball_size", "purity", "radius", "refinement_depth", "normalized_distance", "attack_score"])
        x = pd.DataFrame({"log_ball_size": np.log1p(data.ball_size), "purity": data.purity, "radius": data.radius, "refinement_depth": data.refinement_depth, "normalized_distance": data.normalized_distance})
        if len(data) < len(names) + 5 or any(x[column].nunique() < 2 for column in x):
            continue
        scaled = StandardScaler().fit_transform(x)
        model = LinearRegression().fit(scaled, data.attack_score)
        correlations = {name: spearmanr(x[name], data.attack_score).statistic for name in names}
        rows.append({"method": method, "n": len(data), "r_squared": float(model.score(scaled, data.attack_score)), **{f"coef_{name}": float(value) for name, value in zip(names, model.coef_, strict=True)}, **{f"spearman_{name}": float(value) for name, value in correlations.items()}})
    return pd.DataFrame(rows)
