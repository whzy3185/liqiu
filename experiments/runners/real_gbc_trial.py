"""Clean-room/author-consistent GBC validation on public OpenML data."""
from __future__ import annotations
from typing import Any,Mapping
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from sklearn.svm import SVC
from baselines.gbc import ConfidenceBoundGranularBallClassifier,GranularBallClassifier

def _ece(y,prob,bins=10):
 confidence=np.maximum(prob,1-prob); correct=(prob>=.5)==y; edges=np.linspace(0,1,bins+1); total=len(y); value=0.0
 for lo,hi in zip(edges[:-1],edges[1:]):
  mask=(confidence>=lo)&(confidence<(hi if hi<1 else hi+1e-12))
  if mask.any(): value+=mask.sum()/total*abs(correct[mask].mean()-confidence[mask].mean())
 return float(value)
def run(config:Mapping[str,Any]):
 seed=int(config['seed']); p=config['dataset_generation_parameters']; bundle=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto')
 X=np.asarray(bundle.data,float); y=LabelEncoder().fit_transform(bundle.target); max_samples=int(p.get('max_samples',len(y)))
 if len(y)>max_samples:
  selected,_=train_test_split(np.arange(len(y)),train_size=max_samples,stratify=y,random_state=seed); X,y=X[selected],y[selected]
 X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.3,stratify=y,random_state=seed)
 imputer=SimpleImputer(strategy='median'); scaler=MinMaxScaler(); X_train=scaler.fit_transform(imputer.fit_transform(X_train)); X_test=scaler.transform(imputer.transform(X_test))
 if config['hyperparameters'].get('stop_rule')=='wilson_lower':
  model=ConfidenceBoundGranularBallClassifier(purity=float(config['hyperparameters'].get('purity',.85))).fit(X_train,y_train)
 else: model=GranularBallClassifier(purity=float(config['hyperparameters'].get('purity',.85))).fit(X_train,y_train)
 predicted=model.predict(X_test); probability=model.predict_proba(X_test)[:,1]
 refs={'RandomForestClassifier':RandomForestClassifier(n_estimators=200,min_samples_leaf=2,n_jobs=1,random_state=seed),
       'RBF-SVM':SVC(C=1,gamma='scale'),'5-NN':KNeighborsClassifier(5)}; ref_metrics={}
 for name,ref in refs.items():
  rp=ref.fit(X_train,y_train).predict(X_test); ref_metrics[name]={'accuracy':float(accuracy_score(y_test,rp)),'macro_f1':float(f1_score(y_test,rp,average='macro'))}
 best=max(ref_metrics,key=lambda n:ref_metrics[n]['accuracy']); structure=model.get_structure(); sizes=[len(x) for x in structure['members']]; purities=structure['purity']
 return {'metrics':{'accuracy':float(accuracy_score(y_test,predicted)),'macro_f1':float(f1_score(y_test,predicted,average='macro')),
  'auroc':float(roc_auc_score(y_test,probability)),'calibration_error':_ece(y_test,probability),
  'additional':{'reference':best,'reference_accuracy':ref_metrics[best]['accuracy'],'accuracy_gap':float(accuracy_score(y_test,predicted)-ref_metrics[best]['accuracy']),
                'all_references':ref_metrics,'stop_rule':config['hyperparameters'].get('stop_rule','observed_purity'),'openml_version':bundle.details.get('version'),'openml_md5':bundle.details.get('md5_checksum'),'used_samples':len(y),'source_samples':len(bundle.target)}},
  'structure':{'granule_count':len(sizes),'average_granule_size':float(np.mean(sizes)),
               'uncertain_sample_ratio':float(sum(s for s,q in zip(sizes,purities) if q<.85)/sum(sizes)),
               'additional':{'ball_sizes':sizes,'ball_purities':purities.tolist(),
                             'weighted_impurity':float(sum(s*(1-q) for s,q in zip(sizes,purities))/sum(sizes))}},
  'outcome':'success','notes':'Exploration-pool real-data run using clean-room GBC verified against author boundary-distance code.'}
