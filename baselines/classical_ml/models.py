"""Uniform fit/predict/predict_proba/get_structure classical baselines."""
import numpy as np
from sklearn.cluster import DBSCAN,KMeans
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import AdaBoostClassifier,RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

class _Classifier:
 estimator_cls=None
 def __init__(self,**kwargs):self.kwargs=kwargs;self.model=None
 def fit(self,X,y):self.model=self.estimator_cls(**self.kwargs).fit(X,y);return self
 def predict(self,X):return self.model.predict(X)
 def predict_proba(self,X):return self.model.predict_proba(X)
 def get_structure(self):return {'type':type(self.model).__name__,'classes':self.model.classes_.copy(),'parameters':self.model.get_params(deep=False)}
class KNNAdapter(_Classifier):estimator_cls=KNeighborsClassifier
class SVMAdapter(_Classifier):
 estimator_cls=SVC
 def fit(self,X,y):self.model=CalibratedClassifierCV(SVC(**self.kwargs),method='sigmoid',cv=3,ensemble=False).fit(X,y);return self
class RandomForestAdapter(_Classifier):estimator_cls=RandomForestClassifier
class AdaBoostAdapter(_Classifier):estimator_cls=AdaBoostClassifier

class KMeansAdapter:
 def __init__(self,n_clusters=2,random_state=42,**kwargs):self.n_clusters=n_clusters;self.random_state=random_state;self.kwargs=kwargs
 def fit(self,X,y=None):self.X_=np.asarray(X,float);self.model=KMeans(self.n_clusters,random_state=self.random_state,**self.kwargs).fit(self.X_);return self
 def predict(self,X):return self.model.predict(X)
 def predict_proba(self,X):
  d=self.model.transform(X);z=np.exp(-(d-d.min(1,keepdims=True)));return z/z.sum(1,keepdims=True)
 def get_structure(self):
  labels=self.model.labels_;return {'type':'KMeans','centers':self.model.cluster_centers_.copy(),'members':[np.flatnonzero(labels==k) for k in range(self.n_clusters)],'inertia':float(self.model.inertia_)}

class DBSCANAdapter:
 def __init__(self,eps=.5,min_samples=5,**kwargs):self.eps=eps;self.min_samples=min_samples;self.kwargs=kwargs
 def fit(self,X,y=None):
  self.X_=np.asarray(X,float);self.model=DBSCAN(eps=self.eps,min_samples=self.min_samples,**self.kwargs).fit(self.X_);self.labels_=np.unique(self.model.labels_);self.core_X_=self.X_[self.model.core_sample_indices_];self.core_labels_=self.model.labels_[self.model.core_sample_indices_];return self
 def predict(self,X):
  X=np.asarray(X,float)
  if not len(self.core_X_):return np.full(len(X),-1,int)
  d=np.linalg.norm(X[:,None,:]-self.core_X_[None,:,:],axis=2);i=np.argmin(d,axis=1);return np.where(d[np.arange(len(X)),i]<=self.eps,self.core_labels_[i],-1)
 def predict_proba(self,X):
  pred=self.predict(X);out=np.zeros((len(pred),len(self.labels_)))
  for j,label in enumerate(self.labels_):out[:,j]=pred==label
  return out
 def get_structure(self):return {'type':'DBSCAN','labels':self.labels_.copy(),'core_indices':self.model.core_sample_indices_.copy(),'members':[np.flatnonzero(self.model.labels_==k) for k in self.labels_],'eps':self.eps,'min_samples':self.min_samples}
