"""Clean-room, sklearn-style implementation of the original purity-split GBC."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans

@dataclass
class Ball:
 members: np.ndarray; center: np.ndarray; radius: float; label: object; purity: float; class_counts: np.ndarray

class GranularBallClassifier:
 """Original GBC split and boundary-distance classifier.

 Split k equals the number of labels in an impure ball, k-means uses the author
 code's fixed random_state=5, radius is mean member distance, and prediction
 minimizes ||x-center|| - radius.
 """
 def __init__(self,purity:float=.85,min_samples:int=1,random_state:int=5):
  self.purity=purity; self.min_samples=min_samples; self.random_state=random_state
 def _make_ball(self,indices):
  X=self.X_[indices]; y=self.y_[indices]; center=X.mean(0); distances=np.linalg.norm(X-center,axis=1)
  counts=np.array([np.sum(y==c) for c in self.classes_]); best=int(np.argmax(counts))
  return Ball(np.asarray(indices),center,float(distances.mean()),self.classes_[best],float(counts[best]/len(indices)),counts)
 def _should_stop(self,ball): return ball.purity>=self.purity
 def fit(self,X,y):
  self.X_=np.asarray(X,float); self.y_=np.asarray(y); self.classes_=np.unique(self.y_)
  pending=[self._make_ball(np.arange(len(self.y_)))]; final=[]
  while pending:
   ball=pending.pop(0); labels=np.unique(self.y_[ball.members])
   if self._should_stop(ball) or len(ball.members)<=self.min_samples or len(labels)<2:
    final.append(ball); continue
   assignments=KMeans(n_clusters=len(labels),random_state=self.random_state,n_init='auto').fit_predict(self.X_[ball.members])
   children=[self._make_ball(ball.members[assignments==k]) for k in range(len(labels)) if np.any(assignments==k)]
   if len(children)<2: final.append(ball)
   else: pending=children+pending
  self.balls_=final; return self
 def _boundary_distances(self,X):
  X=np.asarray(X,float); centers=np.vstack([b.center for b in self.balls_]); radii=np.array([b.radius for b in self.balls_])
  return np.linalg.norm(X[:,None,:]-centers[None,:,:],axis=2)-radii
 def predict(self,X):
  nearest=np.argmin(self._boundary_distances(X),axis=1); return np.array([self.balls_[i].label for i in nearest])
 def predict_proba(self,X):
  nearest=np.argmin(self._boundary_distances(X),axis=1); result=[]
  for i in nearest:
   counts=self.balls_[i].class_counts.astype(float); result.append(counts/counts.sum())
  return np.vstack(result)
 def get_structure(self):
  return {"granules":[{"members":b.members.tolist(),"center":b.center.tolist(),"radius":b.radius,
           "label":b.label.item() if hasattr(b.label,'item') else b.label,"purity":b.purity} for b in self.balls_],
          "centers":np.vstack([b.center for b in self.balls_]),"radii":np.array([b.radius for b in self.balls_]),
          "members":[b.members.copy() for b in self.balls_],"purity":np.array([b.purity for b in self.balls_]),
          "labels":np.array([b.label for b in self.balls_]),"uncertainty":np.array([1-b.purity for b in self.balls_])}

class ConfidenceBoundGranularBallClassifier(GranularBallClassifier):
 """Cheap-test M01: stop only when a one-sided Wilson lower bound reaches target."""
 def __init__(self,purity=.85,min_samples=1,random_state=5,z=1.6448536269514722):
  super().__init__(purity,min_samples,random_state); self.z=z
 def _should_stop(self,ball):
  n=len(ball.members); p=ball.purity; z2=self.z*self.z
  lower=(p+z2/(2*n)-self.z*np.sqrt(p*(1-p)/n+z2/(4*n*n)))/(1+z2/n)
  return lower>=self.purity
