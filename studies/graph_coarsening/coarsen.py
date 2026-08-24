"""Frozen random and graph-matching coarsening controls."""
import numpy as np
import scipy.sparse as sp
def identity_assignment(n):return np.arange(n,dtype=int)
def random_assignment(n,k,seed):
 rng=np.random.default_rng(seed);order=rng.permutation(n);assignment=np.empty(n,int);assignment[order]=np.arange(n)%k;return assignment
def heavy_edge_assignment(adj,k,seed):
 n=adj.shape[0];pairs=n-k
 if pairs<=0:return identity_assignment(n)
 rng=np.random.default_rng(seed);used=np.zeros(n,bool);mate=np.full(n,-1,int);made=0
 for i in rng.permutation(n):
  if used[i] or made>=pairs:continue
  neighbors=adj.indices[adj.indptr[i]:adj.indptr[i+1]];available=neighbors[~used[neighbors]]
  if len(available):
   j=int(rng.choice(available));used[i]=used[j]=True;mate[i]=j;mate[j]=i;made+=1
 if made<pairs:
  remaining=np.flatnonzero(~used)
  for i,j in zip(remaining[::2],remaining[1::2]):
   if made>=pairs:break
   used[i]=used[j]=True;mate[i]=j;mate[j]=i;made+=1
 assignment=np.full(n,-1,int);group=0
 for i in range(n):
  if assignment[i]>=0:continue
  assignment[i]=group
  if mate[i]>=0:assignment[mate[i]]=group
  group+=1
 return assignment
def coarsen_graph(features,adjacency,labels,train_idx,assignment):
 n=assignment.max()+1;counts=np.bincount(assignment,minlength=n).astype(float);P=sp.csr_matrix((np.ones(len(assignment)),(assignment,np.arange(len(assignment)))),shape=(n,len(assignment)));X=P@features;X=sp.diags(1/counts)@X;A=(P@adjacency@P.T).tocsr();A.setdiag(0);A.eliminate_zeros();A.data=np.ones_like(A.data);train_set=set(map(int,train_idx));train_labels=np.full(n,-1,int)
 for g in range(n):
  members=np.flatnonzero(assignment==g);known=[i for i in members if i in train_set]
  if known:
   values,c=np.unique(labels[known],return_counts=True);train_labels[g]=values[np.argmax(c)]
 train_groups=np.flatnonzero(train_labels>=0);return {'features':X,'adjacency':A,'train_labels':train_labels,'train_groups':train_groups,'assignment':assignment,'counts':counts}
