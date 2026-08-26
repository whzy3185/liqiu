"""Run label-free recursive balls versus matched KMeans structural features."""
from __future__ import annotations

import json
import sys
import time
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
from applications.models import conventional_models
from gb_application.models import append_gb_features
from gb_application.unsupervised import MatchedKMeansRegions, RecursiveBallCover, uniform_fit_subset, unsupervised_features


RAW = ROOT / "results" / "application_scout" / "raw_baselines.parquet"
OUTPUT = ROOT / "results" / "application_scout" / "unsupervised_local_structure.csv"
AUDIT = ROOT / "results" / "application_scout" / "unsupervised_local_structure_audit.json"
DATASETS = ("steel_plates", "secom", "aps_failure")
SEEDS = (1, 7, 21, 42, 2026)
MODELS = {"xgboost", "lightgbm", "catboost", "random_forest", "extra_trees"}


def main() -> int:
    raw = pd.read_parquet(RAW)
    rows = raw[raw.model.isin(MODELS)].copy().assign(variant="raw").to_dict("records")
    audits = {}
    for dataset_name in DATASETS:
        for seed in SEEDS:
            split = load_industrial_split(dataset_name, seed, ROOT / "data" / "industrial_fault" / "cache" / "openml")
            imputer = SimpleImputer(strategy="median", keep_empty_features=True).fit(split.X_train)
            X_train, X_validation, X_test = [imputer.transform(x) for x in (split.X_train, split.X_validation, split.X_test)]
            scaler = StandardScaler().fit(X_train)
            X_train, X_validation, X_test = [scaler.transform(x) for x in (X_train, X_validation, X_test)]
            subset = uniform_fit_subset(len(X_train), 12_000 if dataset_name == "aps_failure" else None, seed)
            started = time.perf_counter()
            ball = RecursiveBallCover(max_regions=128, min_samples=20, random_state=seed).fit(X_train[subset])
            kmeans = MatchedKMeansRegions(len(ball.regions_), random_state=seed).fit(X_train[subset])
            feature_seconds = time.perf_counter() - started
            variants = {
                "ugbfeat": (append_gb_features(X_train, unsupervised_features(ball, X_train)), append_gb_features(X_test, unsupervised_features(ball, X_test))),
                "kmeansfeat": (append_gb_features(X_train, unsupervised_features(kmeans, X_train)), append_gb_features(X_test, unsupervised_features(kmeans, X_test))),
            }
            audits[f"{dataset_name}:s{seed}"] = {"label_free_fit_subset": len(subset), "n_regions": len(ball.regions_), "kmeans_regions": len(kmeans.centers_)}
            classes = {int(label): int((split.y_train == label).sum()) for label in np.unique(split.y_train)}
            for variant, (train, test) in variants.items():
                for spec in conventional_models(seed, len(classes), class_counts=classes):
                    if spec.name not in MODELS:
                        continue
                    started = time.perf_counter(); spec.estimator.fit(train, split.y_train); fit_seconds=time.perf_counter()-started
                    started = time.perf_counter(); prediction=np.asarray(spec.estimator.predict(test)).reshape(-1); predict_seconds=time.perf_counter()-started
                    rows.append({
                        "experiment":"unsupervised_local_structure_v1","domain":"industrial_tabular","dataset":dataset_name,"seed":seed,"model":spec.name,"variant":variant,
                        "fit_samples":len(split.y_train),"train_samples":len(split.y_train),"test_samples":len(split.y_test),"n_features":train.shape[1],"fit_seconds":fit_seconds,"predict_seconds":predict_seconds,
                        "gb_feature_seconds":feature_seconds,"n_regions":len(ball.regions_),"fit_subset":len(subset),"split_protocol":split.split_protocol,
                        **industrial_metrics(split.y_test,prediction),
                    })
                    print(dataset_name,seed,spec.name,variant,f"F1={rows[-1]['macro_f1']:.4f}",flush=True)
    pd.DataFrame(rows).sort_values(["dataset","seed","model","variant"]).to_csv(OUTPUT,index=False)
    AUDIT.write_text(json.dumps(audits,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__": raise SystemExit(main())

