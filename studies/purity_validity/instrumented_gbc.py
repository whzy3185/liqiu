"""Audited hierarchy wrapper reproducing the clean-room GBC construction."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from sklearn.cluster import KMeans
from baselines.gbc.model import Ball

@dataclass
class ConstructionNode:
    node_id:int; parent_id:int|None; depth:int; members:np.ndarray; center:np.ndarray; radius:float; label:object; purity:float; class_counts:np.ndarray
    children:list['ConstructionNode']=field(default_factory=list); split_centers:np.ndarray|None=None; split_labels:np.ndarray|None=None

class InstrumentedGranularBallClassifier:
    def __init__(self,purity=.85,min_samples=1,random_state=5): self.purity=purity;self.min_samples=min_samples;self.random_state=random_state
    def _node(self,members,parent,depth):
        x=self.X_[members];y=self.y_[members];center=x.mean(0);radius=float(np.linalg.norm(x-center,axis=1).mean());counts=np.array([np.sum(y==c) for c in self.classes_]);best=int(np.argmax(counts))
        node=ConstructionNode(len(self.nodes_),parent,depth,np.asarray(members),center,radius,self.classes_[best],float(counts[best]/len(members)),counts);self.nodes_.append(node);return node
    def fit(self,X,y):
        self.X_=np.asarray(X,float);self.y_=np.asarray(y);self.classes_=np.unique(self.y_);self.nodes_=[];pending=[self._node(np.arange(len(y)),None,0)];terminal=[]
        while pending:
            node=pending.pop(0);labels=np.unique(self.y_[node.members])
            if node.purity>=self.purity or len(node.members)<=self.min_samples or len(labels)<2: terminal.append(node);continue
            km=KMeans(n_clusters=len(labels),random_state=self.random_state,n_init='auto').fit(self.X_[node.members]);node.split_centers=km.cluster_centers_.copy();node.split_labels=km.labels_.copy()
            node.children=[self._node(node.members[km.labels_==k],node.node_id,node.depth+1) for k in range(len(labels)) if np.any(km.labels_==k)]
            if len(node.children)<2: terminal.append(node)
            else: pending=node.children+pending
        self.terminal_nodes_=terminal;self.balls_=[Ball(n.members,n.center,n.radius,n.label,n.purity,n.class_counts) for n in terminal];return self
    def _native(self,X):
        centers=np.vstack([b.center for b in self.balls_]);radii=np.array([b.radius for b in self.balls_]);return np.argmin(np.linalg.norm(np.asarray(X)[:,None,:]-centers[None,:,:],axis=2)-radii,axis=1)
    def route_construction(self,X):
        terminal={n.node_id:i for i,n in enumerate(self.terminal_nodes_)};out=[]
        for row in np.asarray(X,float):
            node=self.nodes_[0]
            while node.node_id not in terminal:
                node=node.children[int(np.argmin(np.linalg.norm(node.split_centers-row,axis=1)))]
            out.append(terminal[node.node_id])
        return np.asarray(out)
    def route_native(self,X): return self._native(X)
    def predict(self,X): return np.asarray([self.balls_[i].label for i in self._native(X)])
