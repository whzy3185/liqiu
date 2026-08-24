"""Author accelerated-GB generation on public data with boundary prediction."""
import importlib.util,random,subprocess
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from sklearn.cluster import k_means
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from sklearn.svm import SVC
from experiments.runners.real_gbc_trial import _ece
ROOT=Path(__file__).resolve().parents[2]
def load(path):
 spec=importlib.util.spec_from_file_location('author_accelerated_gb',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def run(config:Mapping[str,Any]):
 seed=int(config['seed']); random.seed(seed); np.random.seed(seed); p=config['dataset_generation_parameters']; b=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto')
 X=np.asarray(b.data,float); y=LabelEncoder().fit_transform(b.target); cap=int(p.get('max_samples',len(y)))
 if len(y)>cap:
  idx,_=train_test_split(np.arange(len(y)),train_size=cap,stratify=y,random_state=seed); X,y=X[idx],y[idx]
 Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.3,stratify=y,random_state=seed); imp=SimpleImputer(strategy='median'); scale=MinMaxScaler(); Xtr=scale.fit_transform(imp.fit_transform(Xtr)); Xte=scale.transform(imp.transform(Xte))
 path=(ROOT/config['upstream_path']).resolve(); actual=subprocess.run(['git','rev-parse','HEAD'],cwd=path.parent,text=True,stdout=subprocess.PIPE,check=True).stdout.strip()
 if actual!=config['upstream_commit']: raise RuntimeError('upstream commit mismatch')
 m=load(path); data=np.column_stack([ytr,Xtr]); center=data[random.randrange(len(data))]; distances=[m.calculate_distances(row[1:],center[1:]) for row in data]; key='_'.join(str(float(v)) for v in center)
 gb=m.splits(float(config['hyperparameters']['purity']),{key:[data,distances]}); centers=[]
 for k in gb:
  centers.append([float(v) for v in k.split('_')][1:])
 assignments=k_means(X=data[:,1:],n_clusters=len(centers),n_init=2,init=np.asarray(centers),random_state=5)[1]
 balls=[data[assignments==i] for i in range(len(centers))]; bc=np.vstack([x[:,1:].mean(0) for x in balls]); radii=np.array([np.linalg.norm(x[:,1:]-x[:,1:].mean(0),axis=1).mean() for x in balls]); labels=[]; purities=[]
 for x in balls:
  v,c=np.unique(x[:,0],return_counts=True); labels.append(v[np.argmax(c)]); purities.append(float(c.max()/len(x)))
 distance=np.linalg.norm(Xte[:,None,:]-bc[None,:,:],axis=2)-radii; nearest=np.argmin(distance,axis=1); pred=np.asarray(labels)[nearest]; prob=np.asarray(purities)[nearest]*pred+(1-np.asarray(purities)[nearest])*(1-pred)
 refs={'RandomForestClassifier':RandomForestClassifier(n_estimators=200,min_samples_leaf=2,n_jobs=1,random_state=seed),'RBF-SVM':SVC(),'5-NN':KNeighborsClassifier(5)}; metrics={}
 for name,ref in refs.items():
  rp=ref.fit(Xtr,ytr).predict(Xte); metrics[name]={'accuracy':float(accuracy_score(yte,rp)),'macro_f1':float(f1_score(yte,rp,average='macro'))}
 best=max(metrics,key=lambda n:metrics[n]['accuracy']); sizes=[len(x) for x in balls]
 return {'metrics':{'accuracy':float(accuracy_score(yte,pred)),'macro_f1':float(f1_score(yte,pred,average='macro')),'auroc':float(roc_auc_score(yte,prob)),'calibration_error':_ece(yte,prob),
  'additional':{'reference':best,'reference_accuracy':metrics[best]['accuracy'],'accuracy_gap':float(accuracy_score(yte,pred)-metrics[best]['accuracy']),'all_references':metrics}},
  'structure':{'granule_count':len(balls),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':float(sum(s for s,q in zip(sizes,purities) if q<float(config['hyperparameters']['purity']))/sum(sizes)),
               'additional':{'ball_sizes':sizes,'ball_purities':purities,'weighted_impurity':float(sum(s*(1-q) for s,q in zip(sizes,purities))/sum(sizes))}},
  'outcome':'success','notes':'Author accelerated full-dimensional generation plus author boundary-distance classification; exploration purity scan.'}
