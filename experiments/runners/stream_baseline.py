"""Prequential frozen controls for streaming drift."""
import time
from typing import Any,Mapping
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score,f1_score,recall_score
from baselines.gbc import GranularBallClassifier
from counterexamples.generators import generate_stream
def run(config:Mapping[str,Any]):
 seed=int(config['seed']);p=config['dataset_generation_parameters'];X,y,t,meta=generate_stream(p['kind'],p['n_steps'],p['samples_per_step'],seed,p['ambient_dimension'],p['drift_strength']);strategy=config['hyperparameters']['strategy'];classes=np.array([0,1,2]) if p['kind']=='emerging_class' else np.array([0,1]);batch=[];update_time=0.;granules=[];model=None
 first=t==0
 if strategy=='sgd_online':model=SGDClassifier(loss='log_loss',random_state=seed).partial_fit(X[first],y[first],classes=classes)
 else:model=GranularBallClassifier(.85).fit(X[first],y[first]);granules.append(len(model.balls_))
 for step in range(1,p['n_steps']):
  mask=t==step;pred=model.predict(X[mask]);entry={'step':step,'accuracy':float(accuracy_score(y[mask],pred)),'macro_f1':float(f1_score(y[mask],pred,average='macro',zero_division=0))}
  if p['kind']=='emerging_class' and np.any(y[mask]==2):entry['emerging_recall']=float(recall_score(y[mask],pred,labels=[2],average='macro',zero_division=0))
  batch.append(entry);start=time.perf_counter()
  if strategy=='full_rebuild':sel=t<=step;model=GranularBallClassifier(.85).fit(X[sel],y[sel]);granules.append(len(model.balls_))
  elif strategy=='sliding_rebuild':sel=(t<=step)&(t>=max(0,step-2));model=GranularBallClassifier(.85).fit(X[sel],y[sel]);granules.append(len(model.balls_))
  elif strategy=='sgd_online':model.partial_fit(X[mask],y[mask]);
  elif strategy!='no_update':raise ValueError(strategy)
  update_time+=time.perf_counter()-start
 mean_acc=float(np.mean([b['accuracy'] for b in batch]));mean_f1=float(np.mean([b['macro_f1'] for b in batch]));em=[b['emerging_recall'] for b in batch if 'emerging_recall'in b]
 return {'metrics':{'accuracy':mean_acc,'macro_f1':mean_f1,'auroc':None,'calibration_error':None,'additional':{'batch_metrics':batch,'total_update_seconds':update_time,'mean_update_seconds':update_time/(p['n_steps']-1),'emerging_class_recall':float(np.mean(em)) if em else None}},
  'structure':{'granule_count':float(np.mean(granules)) if granules else None,'average_granule_size':None,'uncertain_sample_ratio':None,'additional':{'granule_counts':granules,'max_granules':max(granules) if granules else None,'strategy':strategy}},'outcome':'success','notes':'Prequential stream control; predict batch before update.'}
