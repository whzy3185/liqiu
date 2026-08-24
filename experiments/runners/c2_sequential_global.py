"""Candidate 2 global negative control: sequential three-way evidence acquisition."""
from typing import Any,Mapping
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,brier_score_loss,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from baselines.gbc import GranularBallClassifier
from experiments.runners.real_gbc_trial import _ece
PURITIES=(.60,.70,.80,.90,.95,1.0)
def bound(values,delta):
 n=len(values);mean=float(np.mean(values));var=float(np.var(values,ddof=1)) if n>1 else .25;log=np.log(3/delta);radius=float(np.sqrt(2*var*log/n)+3*log/n);return mean-radius,mean+radius,mean,radius
def run(config:Mapping[str,Any]):
 seed=int(config['seed']);p=config['dataset_generation_parameters'];b=fetch_openml(data_id=int(p['openml_data_id']),as_frame=False,parser='auto');X=np.asarray(b.data,float);y=LabelEncoder().fit_transform(b.target);cap=int(p['max_samples'])
 if len(y)>cap:
  idx,_=train_test_split(np.arange(len(y)),train_size=cap,stratify=y,random_state=seed);X,y=X[idx],y[idx]
 Xdev,Xtest_raw,ydev,ytest=train_test_split(X,y,test_size=.25,stratify=y,random_state=seed);Xtrain,Xval,ytrain,yval=train_test_split(Xdev,ydev,test_size=1/3,stratify=ydev,random_state=seed);imp=SimpleImputer(strategy='median');scale=MinMaxScaler();Xtrain=scale.fit_transform(imp.fit_transform(Xtrain));Xval=scale.transform(imp.transform(Xval));base=GranularBallClassifier(.85).fit(Xtrain,ytrain);base_loss=(base.predict(Xval)!=yval).astype(float);models={};diffs={}
 for purity in PURITIES:
  m=GranularBallClassifier(purity).fit(Xtrain,ytrain);models[purity]=m;diffs[purity]=base_loss-(m.predict(Xval)!=yval).astype(float)
 rng=np.random.default_rng(seed);order=rng.permutation(len(yval));delta=float(config['hyperparameters']['delta']);lam=float(config['hyperparameters']['ball_cost_lambda']);checkpoints=sorted(set([min(k,len(order)) for k in (50,100,200,400,800,1600,len(order))]));history=[];chosen=.85;stop_n=len(order);final_states={}
 for n in checkpoints:
  states={};accepted=[]
  for purity in PURITIES:
   l,u,mean,rad=bound(diffs[purity][order[:n]],delta);threshold=lam*(len(models[purity].balls_)-len(base.balls_))/len(ytrain);state='ACCEPT' if l>threshold else ('REJECT' if u<threshold else 'INVESTIGATE');states[purity]={'state':state,'lcb':l,'ucb':u,'mean_gain':mean,'radius':rad,'cost_threshold':threshold,'granules':len(models[purity].balls_)}
   if state=='ACCEPT':accepted.append((l-threshold,-len(models[purity].balls_),purity))
  history.append({'n':n,'states':states})
  if accepted:
   best=max(accepted);other_ucb=max((v['ucb']-v['cost_threshold'] for k,v in states.items() if v['state']=='INVESTIGATE'),default=-np.inf)
   if best[0]>other_ucb:chosen=best[2];stop_n=n;final_states=states;break
  final_states=states
 if chosen==.85:
  accepted=[(v['lcb']-v['cost_threshold'],-v['granules'],k) for k,v in final_states.items() if v['state']=='ACCEPT']
  if accepted:chosen=max(accepted)[2]
 imp2=SimpleImputer(strategy='median');scale2=MinMaxScaler();Xdev=scale2.fit_transform(imp2.fit_transform(Xdev));Xtest=scale2.transform(imp2.transform(Xtest_raw));model=GranularBallClassifier(chosen).fit(Xdev,ydev);pred=model.predict(Xtest);prob=model.predict_proba(Xtest)[:,1];base2=GranularBallClassifier(.85).fit(Xdev,ydev);bp=base2.predict(Xtest);bprob=base2.predict_proba(Xtest)[:,1];s=model.get_structure();sizes=[len(x) for x in s['members']]
 return {'metrics':{'accuracy':float(accuracy_score(ytest,pred)),'macro_f1':float(f1_score(ytest,pred,average='macro')),'auroc':float(roc_auc_score(ytest,prob)),'calibration_error':_ece(ytest,prob),
  'additional':{'selected_purity':chosen,'stop_n':stop_n,'validation_n':len(yval),'observation_fraction':stop_n/len(yval),'final_states':final_states,'history':history,'baseline_accuracy':float(accuracy_score(ytest,bp)),'accuracy_delta':float(accuracy_score(ytest,pred)-accuracy_score(ytest,bp)),'baseline_brier':float(brier_score_loss(ytest,bprob)),'brier_delta':float(brier_score_loss(ytest,prob)-brier_score_loss(ytest,bprob)),'baseline_granules':len(base2.balls_)}},
  'structure':{'granule_count':len(model.balls_),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':0.0,'additional':{'ball_sizes':sizes,'ball_purities':s['purity'].tolist()}},
  'outcome':'success','notes':'Candidate 2 global sequential paired-risk control; insufficient evidence falls back to p=.85.'}
