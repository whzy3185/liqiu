"""Finite-sample verification of the H-003 incompatible-threshold construction."""
from typing import Any,Mapping
import numpy as np
from sklearn.metrics import accuracy_score
from baselines.gbc import GranularBallClassifier
def run(config:Mapping[str,Any]):
 seed=int(config['seed']);rng=np.random.default_rng(seed);p=config['dataset_generation_parameters'];n=int(p['n_train']);nt=int(p['n_test']);q=float(p['majority_probability']);regime=p['regime'];n0=int(round(q*n));y=np.r_[np.zeros(n0,int),np.ones(n-n0,int)];rng.shuffle(y);t0=int(round(q*nt));yt=np.r_[np.zeros(t0,int),np.ones(nt-t0,int)];rng.shuffle(yt)
 if regime=='separable':
  X=np.column_stack([np.where(y==0,-2.,2.)+rng.normal(0,.15,n),rng.normal(0,.15,n)]);Xt=np.column_stack([np.where(yt==0,-2.,2.)+rng.normal(0,.15,nt),rng.normal(0,.15,nt)])
 elif regime=='uninformative':X=rng.normal(size=(n,2));Xt=rng.normal(size=(nt,2))
 else:raise ValueError(regime)
 tau=float(config['hyperparameters']['purity']);m=GranularBallClassifier(tau).fit(X,y);pred=m.predict(Xt);s=m.get_structure();sizes=[len(x) for x in s['members']]
 return {'metrics':{'accuracy':float(accuracy_score(yt,pred)),'macro_f1':None,'auroc':None,'calibration_error':None,'additional':{'bayes_accuracy':1.0 if regime=='separable' else q,'excess_error_vs_bayes':float((1-accuracy_score(yt,pred))-(0 if regime=='separable' else 1-q)),'root_empirical_purity':q}},
  'structure':{'granule_count':len(m.balls_),'average_granule_size':float(np.mean(sizes)),'uncertain_sample_ratio':0.0,'additional':{'ball_sizes':sizes,'ball_purities':s['purity'].tolist()}},'outcome':'success','notes':'Theory-track H-003 incompatible global-purity construction.'}
