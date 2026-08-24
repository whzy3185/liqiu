"""Candidate 4 audit: split conformal efficiency for GBC purity vs RF probabilities."""
from typing import Any,Mapping
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from baselines.gbc import GranularBallClassifier
def conformal(cal_prob,ycal,test_prob,alpha):
 scores=1-cal_prob[np.arange(len(ycal)),ycal];k=min(len(scores),int(np.ceil((len(scores)+1)*(1-alpha))));q=float(np.partition(scores,k-1)[k-1]);sets=(1-test_prob)<=q;return q,sets
def stats(sets,y,point):
 sizes=sets.sum(1);covered=sets[np.arange(len(y)),y];single=sizes==1
 return {'coverage':float(np.mean(covered)),'average_set_size':float(np.mean(sizes)),'singleton_ratio':float(np.mean(single)),'singleton_accuracy':float(np.mean(point[single]==y[single])) if single.any() else None,'empty_ratio':float(np.mean(sizes==0))}
def run(config:Mapping[str,Any]):
 seed=int(config['seed']);p=config['dataset_generation_parameters'];b=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto');X=np.asarray(b.data,float);y=LabelEncoder().fit_transform(b.target);cap=int(p['max_samples'])
 if len(y)>cap:
  idx,_=train_test_split(np.arange(len(y)),train_size=cap,stratify=y,random_state=seed);X,y=X[idx],y[idx]
 Xdev,Xtest,ydev,ytest=train_test_split(X,y,test_size=.25,stratify=y,random_state=seed);Xtrain,Xcal,ytrain,ycal=train_test_split(Xdev,ydev,test_size=1/3,stratify=ydev,random_state=seed);imp=SimpleImputer(strategy='median');scale=MinMaxScaler();Xtrain=scale.fit_transform(imp.fit_transform(Xtrain));Xcal=scale.transform(imp.transform(Xcal));Xtest=scale.transform(imp.transform(Xtest));gb=GranularBallClassifier(.85).fit(Xtrain,ytrain);rf=RandomForestClassifier(n_estimators=300,min_samples_leaf=2,n_jobs=1,random_state=seed).fit(Xtrain,ytrain);alpha=float(config['hyperparameters']['alpha']);gcal=gb.predict_proba(Xcal);gtest=gb.predict_proba(Xtest);rcal=rf.predict_proba(Xcal);rtest=rf.predict_proba(Xtest);gq,gsets=conformal(gcal,ycal,gtest,alpha);rq,rsets=conformal(rcal,ycal,rtest,alpha);gp=np.argmax(gtest,1);rp=np.argmax(rtest,1);gs=stats(gsets,ytest,gp);rs=stats(rsets,ytest,rp);structure=gb.get_structure();sizes=[len(x) for x in structure['members']]
 return {'metrics':{'accuracy':float(accuracy_score(ytest,gp)),'macro_f1':None,'auroc':None,'calibration_error':None,'additional':{'alpha':alpha,'gbc_quantile':gq,'rf_quantile':rq,'gbc_conformal':gs,'rf_conformal':rs,'rf_accuracy':float(accuracy_score(ytest,rp)),'coverage_gap':gs['coverage']-rs['coverage'],'set_size_gap':gs['average_set_size']-rs['average_set_size']}},
  'structure':{'granule_count':len(sizes),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':1-gs['singleton_ratio'],'additional':{'ball_sizes':sizes,'ball_purities':structure['purity'].tolist()}},'outcome':'success','notes':'Candidate 4 split-conformal audit; same split and calibration size for GBC and RF.'}
