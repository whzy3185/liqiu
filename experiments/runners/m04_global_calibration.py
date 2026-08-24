"""M04 global negative control: validation Brier plus ball-cost selection."""
from typing import Any,Mapping
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,brier_score_loss,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from baselines.gbc import GranularBallClassifier
from experiments.runners.real_gbc_trial import _ece
PURITIES=(.60,.70,.80,.85,.90,.95,1.0)
def run(config:Mapping[str,Any]):
 seed=int(config['seed']); p=config['dataset_generation_parameters']; b=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto'); X=np.asarray(b.data,float); y=LabelEncoder().fit_transform(b.target); cap=int(p['max_samples'])
 if len(y)>cap:
  idx,_=train_test_split(np.arange(len(y)),train_size=cap,stratify=y,random_state=seed); X,y=X[idx],y[idx]
 Xdev,Xtest_raw,ydev,ytest=train_test_split(X,y,test_size=.25,stratify=y,random_state=seed); Xtrain,Xval,ytrain,yval=train_test_split(Xdev,ydev,test_size=1/3,stratify=ydev,random_state=seed)
 imp=SimpleImputer(strategy='median'); scale=MinMaxScaler(); Xtrain=scale.fit_transform(imp.fit_transform(Xtrain)); Xval=scale.transform(imp.transform(Xval)); lam=float(config['hyperparameters']['ball_cost_lambda']); path=[]
 for purity in PURITIES:
  model=GranularBallClassifier(purity).fit(Xtrain,ytrain); prob=model.predict_proba(Xval)[:,1]; brier=float(brier_score_loss(yval,prob)); ratio=len(model.balls_)/len(ytrain); path.append({'purity':purity,'validation_brier':brier,'granules':len(model.balls_),'ball_ratio':ratio,'objective':brier+lam*ratio})
 selected=min(path,key=lambda r:(r['objective'],r['granules']))['purity']; imp2=SimpleImputer(strategy='median'); scale2=MinMaxScaler(); Xdev=scale2.fit_transform(imp2.fit_transform(Xdev)); Xtest=scale2.transform(imp2.transform(Xtest_raw))
 model=GranularBallClassifier(selected).fit(Xdev,ydev); pred=model.predict(Xtest); prob=model.predict_proba(Xtest)[:,1]; base=GranularBallClassifier(.85).fit(Xdev,ydev); bp=base.predict(Xtest); bprob=base.predict_proba(Xtest)[:,1]
 s=model.get_structure(); sizes=[len(x) for x in s['members']]
 return {'metrics':{'accuracy':float(accuracy_score(ytest,pred)),'macro_f1':float(f1_score(ytest,pred,average='macro')),'auroc':float(roc_auc_score(ytest,prob)),'calibration_error':_ece(ytest,prob),
  'additional':{'selected_purity':selected,'validation_path':path,'test_brier':float(brier_score_loss(ytest,prob)),'baseline_p085_brier':float(brier_score_loss(ytest,bprob)),
                'brier_delta_vs_fixed':float(brier_score_loss(ytest,prob)-brier_score_loss(ytest,bprob)),'baseline_p085_ece':_ece(ytest,bprob),'ece_delta_vs_fixed':float(_ece(ytest,prob)-_ece(ytest,bprob)),
                'baseline_p085_accuracy':float(accuracy_score(ytest,bp)),'accuracy_delta_vs_fixed':float(accuracy_score(ytest,pred)-accuracy_score(ytest,bp)),'baseline_p085_granules':len(base.balls_)}},
  'structure':{'granule_count':len(model.balls_),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':0.0,'additional':{'ball_sizes':sizes,'ball_purities':s['purity'].tolist()}},
  'outcome':'success','notes':'M04 global nested Brier/ball-cost negative control; test untouched until final evaluation.'}
