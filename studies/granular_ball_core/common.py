"""GB-core stress helpers: two GB generators, fixed decisions, strong references."""
import warnings
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,brier_score_loss,f1_score,log_loss,recall_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from studies.risk_granularity.tree import GranulationTree
TAUS=(.60,.75,.85,.95,1.0)
def ece(y,prob,bins=10):
 confidence=prob.max(1);pred=prob.argmax(1);edges=np.linspace(0,1,bins+1);value=0.
 for lo,hi in zip(edges[:-1],edges[1:]):
  m=(confidence>=lo)&(confidence<(hi if hi<1 else hi+1e-12))
  if m.any():value+=m.mean()*abs((pred[m]==y[m]).mean()-confidence[m].mean())
 return float(value)
def selective(prob,y,coverages=(.5,.7,.9)):
 pred=prob.argmax(1);confidence=prob.max(1);order=np.argsort(-confidence);out=[]
 for coverage in coverages:
  n=max(1,int(round(len(y)*coverage)));idx=order[:n];out.append({'coverage':coverage,'selective_risk':float(np.mean(pred[idx]!=y[idx])),'threshold':float(confidence[idx].min())})
 return out
def classification_metrics(y,prob):
 pred=prob.argmax(1);classes=np.arange(prob.shape[1]);result={'accuracy':float(accuracy_score(y,pred)),'macro_f1':float(f1_score(y,pred,average='macro',zero_division=0)),'nll':float(log_loss(y,np.clip(prob,1e-9,1),labels=classes)),'ece':ece(y,prob),'selective':selective(prob,y)}
 if len(classes)==2:result['brier']=float(brier_score_loss(y,prob[:,1]));result['minority_recall']=float(recall_score(y,pred,pos_label=1,zero_division=0))
 return result
def fit_tree_frontier(Xtrain,ytrain,Xtest,ytest,method,seed,taus=TAUS):
 tree=GranulationTree(random_state=211+seed,split_method=method).fit(Xtrain,ytrain);rows=[]
 for tau in taus:
  prob=tree.predict_proba(Xtest,tau);m=classification_metrics(ytest,prob);leaves=tree.cut(tau);rows.append({'tau':tau,'granules':len(leaves),'fragmentation_ratio':len(leaves)/len(ytrain),'mean_purity':float(np.mean([x.purity for x in leaves])),'mean_size':float(np.mean([len(x.indices) for x in leaves])),**m})
 return rows
def reference_metrics(Xtrain,ytrain,Xtest,ytest,seed):
 models={'RandomForest':RandomForestClassifier(n_estimators=200,min_samples_leaf=2,n_jobs=1,random_state=seed),'RBF-SVM':SVC(C=1,gamma='scale',probability=True,random_state=seed),'5-NN':KNeighborsClassifier(5)};out={}
 for name,model in models.items():
  with warnings.catch_warnings():warnings.simplefilter('ignore');model.fit(Xtrain,ytrain)
  out[name]=classification_metrics(ytest,model.predict_proba(Xtest))
 return out
