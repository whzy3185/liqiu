"""Frozen 60/20/20 fresh-routing purity validity audit on five real datasets."""

from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from scipy.io import arff
from scipy.stats import beta
from sklearn.cluster import KMeans
from sklearn.datasets import load_breast_cancer, load_digits, load_iris, load_wine
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from baselines.gbc import GranularBallClassifier
from studies.purity_validity.adaptive_gbc import AdaptiveGranularBallClassifier


SEEDS = (1, 7, 21)
FIXED_PURITY = 0.90
COVERAGES = (0.80, 0.90)


def _dry_bean(path: Path):
    with zipfile.ZipFile(path) as archive:
        content = archive.read("DryBeanDataset/Dry_Bean_Dataset.arff")
    data, _ = arff.loadarff(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
    names = [name for name in data.dtype.names if name != "Class"]
    X = np.vstack([np.asarray(data[name], dtype=float) for name in names]).T
    y = LabelEncoder().fit_transform(data["Class"].astype(str))
    return X, y


def datasets(root: Path):
    return {
        "iris": (*load_iris(return_X_y=True),),
        "wine": (*load_wine(return_X_y=True),),
        "breast_cancer": (*load_breast_cancer(return_X_y=True),),
        "digits": (*load_digits(return_X_y=True),),
        "dry_bean": _dry_bean(root / "datasets/real/a3_approved/dry_bean.zip"),
    }


def _cap(X, y, limit, seed):
    if len(y) <= limit:
        return X, y
    X_selected, _, y_selected, _ = train_test_split(X, y, train_size=limit, stratify=y, random_state=seed)
    return X_selected, y_selected


def split_three_way(X, y, seed):
    limit = 1800 if len(y) > 1800 else len(y)
    X, y = _cap(X, y, limit, seed)
    Xs, Xtest, ys, ytest = train_test_split(X, y, test_size=0.20, stratify=y, random_state=seed)
    Xstructure, Xcal, ystructure, ycal = train_test_split(Xs, ys, test_size=0.25, stratify=ys, random_state=seed + 101)
    scaler = StandardScaler()
    return (*[scaler.fit_transform(Xstructure), ystructure, scaler.transform(Xcal), ycal, scaler.transform(Xtest), ytest], scaler)


def route_score(model, X):
    route = model.route_native(X) if hasattr(model, "route_native") else np.argmin(model._boundary_distances(X), axis=1)
    labels = np.asarray([ball.label for ball in model.balls_])
    train_purity = np.asarray([ball.purity for ball in model.balls_], dtype=float)
    support = np.asarray([len(ball.members) for ball in model.balls_], dtype=int)
    depths = np.asarray(getattr(model, "depths_", np.full(len(model.balls_), np.nan)), dtype=float)
    return route, labels[route], train_purity, support, depths


def ball_rows(dataset, seed, method, model, Xstructure, Xcal, ycal, Xtest, ytest):
    cal_route, cal_pred, train_purity, support, depths = route_score(model, Xcal)
    test_route, test_pred, _, _, _ = route_score(model, Xtest)
    structure_route, _, _, _, _ = route_score(model, Xstructure)
    construction_owner = np.full(len(Xstructure), -1, dtype=int)
    for ball_id, ball in enumerate(model.balls_):
        members = np.asarray(ball.members, dtype=int)
        members = members[(members >= 0) & (members < len(Xstructure))]
        construction_owner[members] = ball_id
    construction_native_overlap = float(np.mean(structure_route == construction_owner))
    rows = []
    for ball_id in range(len(model.balls_)):
        cal_mask = cal_route == ball_id
        test_mask = test_route == ball_id
        correct_cal = int(np.sum(cal_pred[cal_mask] == ycal[cal_mask]))
        cal_n = int(np.sum(cal_mask))
        correct_test = int(np.sum(test_pred[test_mask] == ytest[test_mask]))
        test_n = int(np.sum(test_mask))
        heldout = correct_cal / cal_n if cal_n else np.nan
        laplace = (correct_cal + 1) / (cal_n + 2)
        wilson = beta.ppf(0.05, correct_cal + 1, cal_n - correct_cal + 1) if cal_n else 0.0
        rows.append({
            "dataset": dataset, "seed": seed, "method": method, "ball_id": ball_id,
            "support_structure": int(support[ball_id]), "depth": float(depths[ball_id]),
            "train_purity": float(train_purity[ball_id]), "cal_n": cal_n, "cal_purity": heldout,
            "laplace_purity": laplace, "wilson_lower": wilson,
            "test_n": test_n, "fresh_correctness": correct_test / test_n if test_n else np.nan,
            "fresh_weight": test_n / len(ytest), "optimism_train": float(train_purity[ball_id] - (correct_test / test_n)) if test_n else np.nan,
            "optimism_cal": float(heldout - (correct_test / test_n)) if cal_n and test_n else np.nan,
            "construction_native_overlap": construction_native_overlap,
        })
    return rows, test_route, test_pred


def _majority_kmeans(Xstructure, ystructure, Xcal, ycal, Xtest, ytest, k, seed, method):
    k = max(2, min(k, len(Xstructure)))
    km = KMeans(n_clusters=k, n_init="auto", random_state=seed).fit(Xstructure)
    train_route = km.labels_
    labels = []
    purity = []
    support = []
    for cluster in range(k):
        mask = train_route == cluster
        values, counts = np.unique(ystructure[mask], return_counts=True)
        labels.append(values[np.argmax(counts)])
        purity.append(counts.max() / counts.sum())
        support.append(mask.sum())
    def route(X): return np.argmin(np.linalg.norm(X[:, None, :] - km.cluster_centers_[None, :, :], axis=2), axis=1)
    cal_route, test_route = route(Xcal), route(Xtest)
    rows = []
    for cluster in range(k):
        cal_mask, test_mask = cal_route == cluster, test_route == cluster
        cal_n, test_n = int(cal_mask.sum()), int(test_mask.sum())
        cc = int(np.sum(ycal[cal_mask] == labels[cluster]))
        ct = int(np.sum(ytest[test_mask] == labels[cluster]))
        fresh = ct / test_n if test_n else np.nan
        rows.append({"dataset": None, "seed": seed, "method": method, "ball_id": cluster,
                     "support_structure": int(support[cluster]), "depth": 0.0, "train_purity": float(purity[cluster]),
                     "cal_n": cal_n, "cal_purity": cc / cal_n if cal_n else np.nan,
                     "laplace_purity": (cc + 1) / (cal_n + 2),
                     "wilson_lower": beta.ppf(.05, cc + 1, cal_n - cc + 1) if cal_n else 0.0,
                     "test_n": test_n, "fresh_correctness": fresh, "fresh_weight": test_n / len(ytest),
                     "optimism_train": float(purity[cluster] - fresh) if test_n else np.nan,
                     "optimism_cal": float((cc / cal_n) - fresh) if cal_n and test_n else np.nan,
                     "construction_native_overlap": 1.0})
    return rows


def _cart_rows(dataset, seed, Xstructure, ystructure, Xcal, ycal, Xtest, ytest, leaves):
    tree = DecisionTreeClassifier(max_leaf_nodes=max(2, leaves), random_state=seed).fit(Xstructure, ystructure)
    train_leaf, cal_leaf, test_leaf = tree.apply(Xstructure), tree.apply(Xcal), tree.apply(Xtest)
    rows = []
    for leaf in np.unique(train_leaf):
        train_mask, cal_mask, test_mask = train_leaf == leaf, cal_leaf == leaf, test_leaf == leaf
        vals, counts = np.unique(ystructure[train_mask], return_counts=True)
        label, p = vals[np.argmax(counts)], counts.max() / counts.sum()
        cal_n, test_n = int(cal_mask.sum()), int(test_mask.sum())
        cc, ct = int(np.sum(ycal[cal_mask] == label)), int(np.sum(ytest[test_mask] == label))
        fresh = ct / test_n if test_n else np.nan
        rows.append({"dataset": dataset, "seed": seed, "method": "cart_matched_leaf_count", "ball_id": int(leaf),
                     "support_structure": int(train_mask.sum()), "depth": np.nan, "train_purity": float(p),
                     "cal_n": cal_n, "cal_purity": cc / cal_n if cal_n else np.nan,
                     "laplace_purity": (cc + 1) / (cal_n + 2),
                     "wilson_lower": beta.ppf(.05, cc + 1, cal_n - cc + 1) if cal_n else 0.0,
                     "test_n": test_n, "fresh_correctness": fresh, "fresh_weight": test_n / len(ytest),
                     "optimism_train": float(p - fresh) if test_n else np.nan,
                     "optimism_cal": float((cc / cal_n) - fresh) if cal_n and test_n else np.nan,
                     "construction_native_overlap": 1.0})
    return rows


def selective_metrics(rows, score_name, coverages=COVERAGES):
    result = []
    for coverage in coverages:
        usable = [row for row in rows if row["cal_n"] > 0 and row["test_n"] > 0]
        ordered = sorted(usable, key=lambda row: (-row[score_name], row["ball_id"]))
        # Use calibration frequencies to set a deterministic ball-score threshold.
        cal_mass = sum(row["cal_n"] for row in ordered)
        running = 0
        threshold = ordered[-1][score_name]
        for row in ordered:
            running += row["cal_n"]
            threshold = row[score_name]
            if running / cal_mass >= coverage:
                break
        accepted = [row for row in usable if row[score_name] >= threshold]
        test_mass = sum(row["test_n"] for row in accepted)
        correct = sum(row["fresh_correctness"] * row["test_n"] for row in accepted)
        result.append({"score": score_name, "target_coverage": coverage, "threshold": threshold,
                       "test_coverage": test_mass / sum(row["test_n"] for row in usable),
                       "test_risk": 1 - correct / test_mass if test_mass else np.nan})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results/oush_adaptive_purity"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_rows, selective = [], []
    for dataset, (X, y) in datasets(Path.cwd()).items():
        for seed in SEEDS:
            Xs, ys, Xc, yc, Xt, yt, _ = split_three_way(X, y, seed)
            fixed = GranularBallClassifier(purity=FIXED_PURITY, random_state=seed).fit(Xs, ys)
            adaptive = AdaptiveGranularBallClassifier(random_state=seed).fit(Xs, ys)
            for method, model in (("gb_fixed_p090", fixed), ("gb_adaptive_parameter_free", adaptive)):
                rows, _, _ = ball_rows(dataset, seed, method, model, Xs, Xc, yc, Xt, yt)
                all_rows.extend(rows)
                for metric in selective_metrics(rows, "train_purity") + selective_metrics(rows, "cal_purity") + selective_metrics(rows, "laplace_purity") + selective_metrics(rows, "wilson_lower"):
                    selective.append({"dataset": dataset, "seed": seed, "method": method, **metric})
            k = len(fixed.balls_)
            kmeans_rows = _majority_kmeans(Xs, ys, Xc, yc, Xt, yt, k, seed, "kmeans_matched_fixed_gb")
            for row in kmeans_rows: row["dataset"] = dataset
            all_rows.extend(kmeans_rows)
            all_rows.extend(_cart_rows(dataset, seed, Xs, ys, Xc, yc, Xt, yt, k))
            k_adaptive = len(adaptive.balls_)
            kmeans_adaptive_rows = _majority_kmeans(Xs, ys, Xc, yc, Xt, yt, k_adaptive, seed, "kmeans_matched_adaptive_gb")
            for row in kmeans_adaptive_rows:
                row["dataset"] = dataset
            all_rows.extend(kmeans_adaptive_rows)
            adaptive_cart_rows = _cart_rows(dataset, seed, Xs, ys, Xc, yc, Xt, yt, k_adaptive)
            for row in adaptive_cart_rows:
                row["method"] = "cart_matched_adaptive_leaf_count"
            all_rows.extend(adaptive_cart_rows)
            print({"dataset": dataset, "seed": seed, "fixed_balls": k, "adaptive_balls": len(adaptive.balls_), "adaptive_cap": adaptive.safety_cap_hit_}, flush=True)

    with (args.output_dir / "ball_level.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader(); writer.writerows(all_rows)
    with (args.output_dir / "selective.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selective[0]))
        writer.writeheader(); writer.writerows(selective)
    manifest = {"seeds": SEEDS, "split": "60/20/20 structure/calibration/test", "fixed_purity": FIXED_PURITY,
                "datasets": list(datasets(Path.cwd())), "methods": ["gb_fixed_p090", "gb_adaptive_parameter_free", "kmeans_matched_fixed_gb", "cart_matched_leaf_count"],
                "routing": "native terminal boundary distance for GB; native leaf routing for CART; nearest center for KMeans"}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
