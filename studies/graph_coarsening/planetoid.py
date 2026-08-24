"""Dependency-light loader for the public Planetoid citation splits."""
import pickle
from pathlib import Path
import numpy as np
import scipy.sparse as sp
def _read(path):
 with path.open('rb') as h:return pickle.load(h,encoding='latin1')
def load_planetoid(root,name):
 root=Path(root);x,tx,allx,y,ty,ally,graph=[_read(root/f'ind.{name}.{part}') for part in ('x','tx','allx','y','ty','ally','graph')];test=np.array([int(x) for x in (root/f'ind.{name}.test.index').read_text().splitlines()]);test_sorted=np.sort(test)
 if name=='citeseer':
  full=np.arange(test.min(),test.max()+1);extended=sp.lil_matrix((len(full),x.shape[1]));extended[test_sorted-full.min()]=tx;tx=extended;ey=np.zeros((len(full),y.shape[1]));ey[test_sorted-full.min()]=ty;ty=ey
 features=sp.vstack((allx,tx)).tolil();features[test,:]=features[test_sorted,:].copy();labels=np.vstack((ally,ty));labels[test,:]=labels[test_sorted,:].copy();n=labels.shape[0];rows=[];cols=[]
 for i,neighbors in graph.items():
  for j in neighbors:
   if i<n and j<n:rows.append(i);cols.append(j)
 adj=sp.coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(n,n));adj=((adj+adj.T)>0).astype(np.float32).tocsr();features=features.tocsr().astype(np.float32);s=np.asarray(features.sum(1)).ravel();inv=np.zeros_like(s);np.divide(1,s,out=inv,where=s>0);features=sp.diags(inv)@features;target=np.argmax(labels,1).astype(np.int64);train=np.arange(len(y));val=np.arange(len(y),min(len(y)+500,n));return {'name':name,'features':features,'adjacency':adj,'labels':target,'train_idx':train,'val_idx':val,'test_idx':test_sorted}
