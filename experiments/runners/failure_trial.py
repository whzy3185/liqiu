"""One reproducible GBC-vs-reference counterexample search trial."""

from __future__ import annotations

import importlib.util
import random
import subprocess
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from counterexamples.generators import generate

ROOT = Path(__file__).resolve().parents[2]

def _load(path, name):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def _verify(path, expected):
    repo=path.parent
    actual=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,stdout=subprocess.PIPE,check=True).stdout.strip()
    if actual != expected: raise RuntimeError(f"upstream commit mismatch: {actual}")

def _purity(ball):
    _, counts=np.unique(ball[:,0],return_counts=True); return float(counts.max()/len(ball))

def _original(module, data, purity):
    balls=[data]
    while True:
        before=len(balls); balls=module.splits(balls,purity=purity,splitting_method="k-means")
        if len(balls)==before: return balls

def _adaptive(module, data, seed):
    random.seed(seed); module.random.seed(seed)
    initial=module.get_label_and_purity(data)[1]; center=data[random.randrange(len(data))]
    distances=[module.calculate_distances(row[1:],center[1:]) for row in data]
    key="_".join(str(float(v)) for v in center)
    result=module.splits(initial,{key:[data,distances]})
    return [value[0] for value in result.values()]

def _predict(balls, X):
    centers=np.vstack([b[:,1:].mean(0) for b in balls])
    radii=np.array([np.linalg.norm(b[:,1:]-b[:,1:].mean(0),axis=1).mean() for b in balls])
    labels=[]
    for b in balls:
        values,counts=np.unique(b[:,0],return_counts=True); labels.append(values[np.argmax(counts)])
    distances=np.linalg.norm(X[:,None,:]-centers[None,:,:],axis=2)-radii[None,:]
    return np.asarray(labels)[np.argmin(distances,axis=1)]

def run(config: Mapping[str,Any]):
    seed=int(config["seed"]); params=dict(config["dataset_generation_parameters"]); family=params.pop("family")
    n=int(params.pop("n_samples")); ambient=int(params.pop("ambient_dimension"))
    X,y,_=generate(family,n_samples=n,seed=seed,ambient_dimension=ambient,**params)
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.3,stratify=y,random_state=seed)
    scaler=MinMaxScaler(); X_train=scaler.fit_transform(X_train); X_test=scaler.transform(X_test)
    path=(ROOT/config["upstream_path"]).resolve(); _verify(path,config["upstream_commit"])
    module=_load(path,f"failure_{config['variant']}_{config['experiment_id']}")
    data=np.column_stack([y_train,X_train])
    if config["variant"]=="original": balls=_original(module,data,float(config["hyperparameters"].get("purity",.85)))
    elif config["variant"]=="adaptive": balls=_adaptive(module,data,seed)
    else: raise ValueError(config["variant"])
    predicted=_predict(balls,X_test); accuracy=float(accuracy_score(y_test,predicted)); macro=float(f1_score(y_test,predicted,average="macro"))
    references={
        "RandomForestClassifier":RandomForestClassifier(n_estimators=150,min_samples_leaf=2,n_jobs=1,random_state=seed),
        "RBF-SVM":SVC(C=1.0,gamma="scale"),
        "5-NN":KNeighborsClassifier(n_neighbors=5),
    }
    reference_metrics={}
    for name,reference in references.items():
        ref_pred=reference.fit(X_train,y_train).predict(X_test)
        reference_metrics[name]={"accuracy":float(accuracy_score(y_test,ref_pred)),
                                 "macro_f1":float(f1_score(y_test,ref_pred,average="macro"))}
    reference_name=max(reference_metrics,key=lambda name:reference_metrics[name]["accuracy"])
    ref_accuracy=reference_metrics[reference_name]["accuracy"]; ref_macro=reference_metrics[reference_name]["macro_f1"]
    eps=1e-3; failure_score=(1-accuracy+eps)/(1-ref_accuracy+eps)
    purities=[_purity(b) for b in balls]; sizes=[len(b) for b in balls]
    uncertain=float(sum(s for s,p in zip(sizes,purities) if p < .85)/sum(sizes))
    return {"metrics":{"accuracy":accuracy,"macro_f1":macro,"auroc":None,"calibration_error":None,
                       "additional":{"reference":reference_name,"reference_accuracy":ref_accuracy,
                                     "reference_macro_f1":ref_macro,"accuracy_gap":accuracy-ref_accuracy,
                                     "failure_score":float(failure_score),"all_references":reference_metrics}},
            "structure":{"granule_count":len(balls),"average_granule_size":float(np.mean(sizes)),
                         "uncertain_sample_ratio":uncertain,"additional":{"ball_sizes":sizes,"ball_purities":purities}},
            "outcome":"success","notes":"Exploration-pool failure-search trial; three references use identical split/scaling and the best held-out accuracy defines the gap."}
