"""Independent maximal granulation tree and reusable purity cuts."""
from dataclasses import dataclass,field
import numpy as np
from sklearn.cluster import KMeans
@dataclass
class Node:
 indices:np.ndarray;center:np.ndarray;radius:float;label:int;purity:float;counts:np.ndarray;children:list=field(default_factory=list)
class GranulationTree:
 def __init__(self,min_samples=2,max_depth=30,random_state=17,split_method='kmeans'):self.min_samples=min_samples;self.max_depth=max_depth;self.random_state=random_state;self.split_method=split_method
 def _node(self,idx):
  X=self.X[idx];y=self.y[idx];center=X.mean(0);values,counts=np.unique(y,return_counts=True);j=int(np.argmax(counts));full=np.array([np.sum(y==c) for c in self.classes]);return Node(idx,center,float(np.linalg.norm(X-center,axis=1).mean()),int(values[j]),float(counts[j]/len(idx)),full)
 def _grow(self,idx,depth):
  node=self._node(idx)
  if node.purity>=1 or len(idx)<=self.min_samples or depth>=self.max_depth:return node
  if self.split_method=='kmeans':labels=KMeans(2,random_state=self.random_state+depth,n_init='auto').fit_predict(self.X[idx])
  elif self.split_method=='class_means':
   classes=np.unique(self.y[idx]);means=np.vstack([self.X[idx][self.y[idx]==c].mean(0) for c in classes])
   # This tree is binary.  For multiclass nodes retain a deterministic
   # class-informed two-center initialization rather than passing an invalid
   # c-by-d array to KMeans(n_clusters=2).  Binary nodes preserve the prior
   # exact two-class-means behavior.
   if len(classes)>2:
    distances=np.linalg.norm(means[:,None,:]-means[None,:,:],axis=2);left,right=np.unravel_index(np.argmax(distances),distances.shape);init=means[[left,right]]
   else:init=means
   labels=KMeans(2,init=init,n_init=1,random_state=self.random_state+depth).fit_predict(self.X[idx])
  else:raise ValueError(self.split_method)
  if len(np.unique(labels))<2:return node
  node.children=[self._grow(idx[labels==k],depth+1) for k in (0,1)];return node
 def fit(self,X,y):self.X=np.asarray(X,float);self.y=np.asarray(y,int);self.classes=np.unique(self.y);self.root=self._grow(np.arange(len(y)),0);return self
 def cut(self,tau):
  leaves=[]
  def visit(n):
   if n.purity>=tau or not n.children:leaves.append(n)
   else:
    for c in n.children:visit(c)
  visit(self.root);return leaves
 def predict_proba(self,X,tau):
  leaves=self.cut(tau);centers=np.vstack([n.center for n in leaves]);radii=np.array([n.radius for n in leaves]);nearest=np.argmin(np.linalg.norm(np.asarray(X)[:,None,:]-centers[None,:,:],axis=2)-radii,axis=1);out=[]
  for i in nearest:
   c=leaves[i].counts.astype(float);out.append(c/c.sum())
  return np.vstack(out)
 def predict(self,X,tau):return self.classes[np.argmax(self.predict_proba(X,tau),axis=1)]
