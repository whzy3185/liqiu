"""B0 shadow-release membership audit for published GBFRS feature selection."""

from __future__ import annotations

import contextlib
import importlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from frlearn.feature_preprocessors import FRFS
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import GroupKFold, StratifiedShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from skrebate import ReliefF


@dataclass(frozen=True)
class SelectionOutput:
    method: str
    selected: np.ndarray
    ranking: np.ndarray | None


def load_dataset(name: str) -> tuple[np.ndarray, np.ndarray, str]:
    if name == "breast_cancer":
        bunch = load_breast_cancer()
        return np.asarray(bunch.data, float), np.asarray(bunch.target, int), "sklearn.load_breast_cancer"
    if name in {"sonar", "spambase"}:
        from ucimlrepo import fetch_ucirepo
        dataset_id = {"sonar": 151, "spambase": 94}[name]
        bunch = fetch_ucirepo(id=dataset_id)
        return np.asarray(bunch.data.features, float), LabelEncoder().fit_transform(np.asarray(bunch.data.targets).reshape(-1)), f"UCI id={dataset_id} via ucimlrepo"
    raise ValueError(f"Unknown B0 dataset {name}")


def gbfrs_select(x: np.ndarray, y: np.ndarray, upstream_dir: Path, seed: int) -> SelectionOutput:
    sys.path.insert(0, str(upstream_dir))
    module = importlib.import_module("GBFRS")
    np.random.seed(seed)
    data = np.column_stack([x, y, np.arange(len(y), dtype=int)])
    with contextlib.redirect_stdout(io.StringIO()):
        ordered = module.attribute_reduce(data, pur=1)
    selected = np.asarray(ordered, dtype=int)
    ranking = np.zeros(x.shape[1], dtype=float)
    ranking[selected] = np.arange(len(selected), 0, -1, dtype=float)
    return SelectionOutput("GBFRS", selected, ranking)


def baseline_selectors(x: np.ndarray, y: np.ndarray, count: int, seed: int) -> list[SelectionOutput]:
    count = max(1, min(count, x.shape[1]))
    frfs = np.flatnonzero(FRFS(n_features=count)(x, y).selection)
    mi = mutual_info_classif(x, y, random_state=seed)
    mi_order = np.argsort(-mi, kind="stable")
    relief = ReliefF(n_features_to_select=count, n_neighbors=min(10, max(1, len(x) - 1)), n_jobs=1).fit(x, y)
    relief_order = np.asarray(relief.top_features_, dtype=int)
    def rank(order: np.ndarray) -> np.ndarray:
        values = np.empty(len(order), dtype=float)
        values[order] = np.arange(len(order), 0, -1, dtype=float)
        return values
    return [
        SelectionOutput("FRFS", frfs, None),
        SelectionOutput("MutualInformation", mi_order[:count], rank(mi_order)),
        SelectionOutput("ReliefF", relief_order[:count], rank(relief_order)),
    ]


def _feature_matrix(output: SelectionOutput, candidate_x: np.ndarray, release: str) -> np.ndarray:
    mask = np.zeros(candidate_x.shape[1], dtype=float)
    mask[output.selected] = 1.0
    if release == "ranking":
        if output.ranking is None:
            raise ValueError("ranking unavailable")
        vector = output.ranking / max(float(output.ranking.max()), 1.0)
    else:
        vector = mask
    interaction = candidate_x * vector[None, :]
    features = [np.tile(vector, (len(candidate_x), 1)), interaction]
    if release == "mask_count":
        features.append(np.full((len(candidate_x), 1), len(output.selected), dtype=float))
    return np.column_stack(features)


def _tpr(y: np.ndarray, score: np.ndarray, fpr_target: float) -> float:
    fpr, tpr, _ = roc_curve(y, score)
    return float(tpr[fpr <= fpr_target].max()) if np.any(fpr <= fpr_target) else 0.0


def _jaccard(outputs: list[SelectionOutput]) -> float:
    values = []
    for i, left in enumerate(outputs):
        for right in outputs[i + 1 :]:
            a, b = set(left.selected.tolist()), set(right.selected.tolist())
            values.append(len(a & b) / len(a | b) if a | b else 1.0)
    return float(np.mean(values)) if values else 1.0


def run_seed(dataset: str, seed: int, upstream_dir: Path, max_pool: int = 600, shadows: int = 24) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    x, y, source = load_dataset(dataset)
    reference_x, pool_x, reference_y, pool_y = train_test_split(x, y, test_size=0.8, stratify=y, random_state=seed)
    if len(pool_x) > max_pool:
        keep, _ = train_test_split(np.arange(len(pool_x)), train_size=max_pool, stratify=pool_y, random_state=seed)
        pool_x, pool_y = pool_x[keep], pool_y[keep]
    reference_scaler = StandardScaler().fit(reference_x)
    attack_candidates = reference_scaler.transform(pool_x)
    splitter = StratifiedShuffleSplit(n_splits=shadows, train_size=0.5, random_state=seed)
    selections: dict[str, list[SelectionOutput]] = {name: [] for name in ("GBFRS", "FRFS", "MutualInformation", "ReliefF")}
    memberships: list[np.ndarray] = []
    shadow_rows: list[dict[str, object]] = []
    for shadow_id, (member, _) in enumerate(splitter.split(pool_x, pool_y)):
        shadow_x = StandardScaler().fit_transform(pool_x[member])
        shadow_y = pool_y[member]
        gbfrs = gbfrs_select(shadow_x, shadow_y, upstream_dir, seed * 1000 + shadow_id)
        outputs = [gbfrs, *baseline_selectors(shadow_x, shadow_y, len(gbfrs.selected), seed * 1000 + shadow_id)]
        membership = np.zeros(len(pool_x), dtype=int)
        membership[member] = 1
        memberships.append(membership)
        for output in outputs:
            selections[output.method].append(output)
            shadow_rows.append({"dataset": dataset, "seed": seed, "shadow_id": shadow_id, "source": source, "method": output.method, "selected_features": output.selected.tolist(), "selected_count": len(output.selected), "ranking_exposed": output.ranking is not None})
    target = np.concatenate(memberships)
    groups = np.repeat(np.arange(shadows), len(pool_x))
    result_rows: list[dict[str, object]] = []
    for method, outputs in selections.items():
        stability = _jaccard(outputs)
        for release in ("mask", "mask_count", "ranking"):
            if release == "ranking" and any(output.ranking is None for output in outputs):
                continue
            features = np.vstack([_feature_matrix(output, attack_candidates, release) for output in outputs])
            for attack in ("logistic", "random_forest"):
                model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, class_weight="balanced")) if attack == "logistic" else RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", n_jobs=1, random_state=seed)
                cv = list(GroupKFold(n_splits=5).split(features, target, groups))
                score = np.empty(len(target), dtype=float)
                for train, test in cv:
                    model.fit(features[train], target[train])
                    score[test] = model.predict_proba(features[test])[:, 1]
                result_rows.append({"dataset": dataset, "source": source, "seed": seed, "method": method, "release": release, "attack": attack, "n_total": len(x), "pool_samples": len(pool_x), "reference_samples": len(reference_x), "feature_count": x.shape[1], "shadow_runs": shadows, "selected_count_mean": float(np.mean([len(output.selected) for output in outputs])), "selection_stability_jaccard": stability, "roc_auc": float(roc_auc_score(target, score)), "pr_auc": float(average_precision_score(target, score)), "tpr_at_1pct_fpr": _tpr(target, score, .01), "tpr_at_0_1pct_fpr": _tpr(target, score, .001) if len(pool_x) >= 1000 else float("nan")})
    return result_rows, shadow_rows
