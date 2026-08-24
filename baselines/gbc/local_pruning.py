"""Cheap-test local stable risk/cost pruning for H-003."""
from dataclasses import dataclass,field
import numpy as np
from sklearn.cluster import KMeans

@dataclass
class Node:
 indices:np.ndarray; center:np.ndarray; radius:float; label:int; purity:float; counts:np.ndarray
 children:list=field(default_factory=list); active_split:bool=False

class StableLocalPrunedGBC:
 def __init__(self,cost_per_leaf=.5,min_train=2,min_validation=20,random_state=5):
  self.cost_per_leaf=cost_per_leaf; self.min_train=min_train; self.min_validation=min_validation; self.random_state=random_state
 def _node(self,idx):
  X=self.X_[idx]; y=self.y_[idx]; c=X.mean(0); counts=np.array([np.sum(y==k) for k in self.classes_]); best=int(np.argmax(counts))
  return Node(np.asarray(idx),c,float(np.linalg.norm(X-c,axis=1).mean()),int(self.classes_[best]),float(counts[best]/len(idx)),counts)
 def _grow(self,idx):
  node=self._node(idx); labels=np.unique(self.y_[idx])
  if node.purity>=1 or len(idx)<=self.min_train or len(labels)<2:return node
  a=KMeans(n_clusters=len(labels),random_state=self.random_state,n_init='auto').fit_predict(self.X_[idx]); children=[self._grow(idx[a==k]) for k in range(len(labels)) if np.any(a==k)]
  if len(children)>1: node.children=children; node.active_split=True
  return node
 def _route_child(self,node,X):
  centers=np.vstack([c.center for c in node.children]); radii=np.array([c.radius for c in node.children]); return np.argmin(np.linalg.norm(X[:,None,:]-centers[None,:,:],axis=2)-radii,axis=1)
 def _predict_node(self,node,X):
  if not node.active_split:return np.full(len(X),node.label,int)
  route=self._route_child(node,X); out=np.empty(len(X),int)
  for k,child in enumerate(node.children):
   mask=route==k
   if mask.any():out[mask]=self._predict_node(child,X[mask])
  return out
 def _leaves(self,node):return sum(self._leaves(c) for c in node.children) if node.active_split else 1
 def _prune(self,node,Xv,yv):
  if not node.children:return
  route=self._route_child(node,Xv) if len(Xv) else np.array([],int)
  for k,child in enumerate(node.children):
   mask=route==k; self._prune(child,Xv[mask],yv[mask])
  node.active_split=True
  if len(yv)<self.min_validation:node.active_split=False;return
  split=self._predict_node(node,Xv); keep=np.full(len(yv),node.label); gain=int(np.sum(keep!=yv)-np.sum(split!=yv)); extra=self._leaves(node)-1
  halves=np.arange(len(yv))%2
  stable=all(np.sum(keep[halves==h]!=yv[halves==h])-np.sum(split[halves==h]!=yv[halves==h])>=0 for h in (0,1))
  if not stable or gain<=self.cost_per_leaf*extra:node.active_split=False
 def fit(self,X,y,validation_data):
  self.X_=np.asarray(X,float); self.y_=np.asarray(y,int); self.classes_=np.unique(self.y_); self.root_=self._grow(np.arange(len(y))); Xv,yv=validation_data; self._prune(self.root_,np.asarray(Xv,float),np.asarray(yv,int));return self
 def predict(self,X):return self._predict_node(self.root_,np.asarray(X,float))
 def _proba_node(self,node,X):
  if not node.active_split:
   p=node.counts/node.counts.sum();return np.tile(p,(len(X),1))
  route=self._route_child(node,X);out=np.empty((len(X),len(self.classes_)))
  for k,c in enumerate(node.children):
   mask=route==k
   if mask.any():out[mask]=self._proba_node(c,X[mask])
  return out
 def predict_proba(self,X):return self._proba_node(self.root_,np.asarray(X,float))
 def get_structure(self):
  leaves=[]
  def visit(n):
   if n.active_split:
    for c in n.children:visit(c)
   else:leaves.append(n)
  visit(self.root_);return {'granule_count':len(leaves),'sizes':[len(n.indices) for n in leaves],'purities':[n.purity for n in leaves]}
