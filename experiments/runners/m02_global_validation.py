"""M02 negative control: nested global validation-risk/ball-cost selection."""
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
from baselines.gbc import GranularBallClassifier
from experiments.runners.real_gbc_trial import _ece
PURITIES=(.60,.70,.80,.85,.90,.95,1.0)
def run(config:Mapping[str,Any]):
 seed=int(config['seed']); p=config['dataset_generation_parameters']; b=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto'); X=np.asarray(b.data,float); y=LabelEncoder().fit_transform(b.target); cap=int(p['max_samples'])
 if len(y)>cap:
  idx,_=train_test_split(np.arange(len(y)),train_size=cap,stratify=y,random_state=seed); X,y=X[idx],y[idx]
 Xdev,Xtest_raw,ydev,ytest=train_test_split(X,y,test_size=.25,stratify=y,random_state=seed); Xtrain,Xval,ytrain,yval=train_test_split(Xdev,ydev,test_size=1/3,stratify=ydev,random_state=seed)
 imp=SimpleImputer(strategy='median'); scale=MinMaxScaler(); Xtrain=scale.fit_transform(imp.fit_transform(Xtrain)); Xval=scale.transform(imp.transform(Xval))
 lam=float(config['hyperparameters']['ball_cost_lambda']); path=[]
 for purity in PURITIES:
  model=GranularBallClassifier(purity).fit(Xtrain,ytrain); acc=float(accuracy_score(yval,model.predict(Xval))); ratio=len(model.balls_)/len(ytrain); path.append({'purity':purity,'validation_accuracy':acc,'granules':len(model.balls_),'ball_ratio':ratio,'utility':acc-lam*ratio})
 selected=max(path,key=lambda r:(r['utility'],-r['granules']))['purity']
 # Refit preprocessing and model on all development data after selection.
 imp2=SimpleImputer(strategy='median'); scale2=MinMaxScaler(); Xdev=scale2.fit_transform(imp2.fit_transform(Xdev)); Xtest2=scale2.transform(imp2.transform(Xtest_raw)); model=GranularBallClassifier(selected).fit(Xdev,ydev); pred=model.predict(Xtest2); prob=model.predict_proba(Xtest2)[:,1]
 baseline=GranularBallClassifier(.85).fit(Xdev,ydev); bp=baseline.predict(Xtest2)
 refs={'RandomForestClassifier':RandomForestClassifier(n_estimators=200,min_samples_leaf=2,n_jobs=1,random_state=seed),'RBF-SVM':SVC(),'5-NN':KNeighborsClassifier(5)}; rm={}
 for name,ref in refs.items():
  rp=ref.fit(Xdev,ydev).predict(Xtest2); rm[name]={'accuracy':float(accuracy_score(ytest,rp)),'macro_f1':float(f1_score(ytest,rp,average='macro'))}
 best=max(rm,key=lambda n:rm[n]['accuracy']); s=model.get_structure(); sizes=[len(x) for x in s['members']]
 return {'metrics':{'accuracy':float(accuracy_score(ytest,pred)),'macro_f1':float(f1_score(ytest,pred,average='macro')),'auroc':float(roc_auc_score(ytest,prob)),'calibration_error':_ece(ytest,prob),
  'additional':{'selected_purity':selected,'validation_path':path,'baseline_p085_accuracy':float(accuracy_score(ytest,bp)),'baseline_p085_granules':len(baseline.balls_),
                'accuracy_delta_vs_fixed':float(accuracy_score(ytest,pred)-accuracy_score(ytest,bp)),'reference':best,'reference_accuracy':rm[best]['accuracy'],'accuracy_gap':float(accuracy_score(ytest,pred)-rm[best]['accuracy']),'all_references':rm}},
  'structure':{'granule_count':len(model.balls_),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':0.0,'additional':{'ball_sizes':sizes,'ball_purities':s['purity'].tolist()}},
  'outcome':'success','notes':'M02 global nested-validation negative control; selection uses validation only and test remains untouched.'}
