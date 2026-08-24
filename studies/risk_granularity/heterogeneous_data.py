"""Independent heterogeneous-region distributions for v2 theory tests."""
import numpy as np
FAMILIES={'A':['separable','null'],'B':['separable','small_margin','null'],'C':['large_margin','small_margin','null','curved'],'D':['large_margin','density','null']}
def _counts(n,regions,w):
 weights=np.array([w]+[(1-w)/(regions-1)]*(regions-1));counts=np.maximum(20,np.floor(n*weights).astype(int));counts[0]+=n-counts.sum();return counts
def _region(kind,n,q,d,noise,rng,offset):
 n0=int(round(q*n));y=np.r_[np.zeros(n0,int),np.ones(n-n0,int)];rng.shuffle(y);X=rng.normal(0,1,(n,d))
 if kind in ('separable','large_margin'):X[:,0]=np.where(y==0,-2.,2.)+rng.normal(0,.2,n)
 elif kind=='small_margin':X[:,0]=np.where(y==0,-.35,.35)+rng.normal(0,.8,n)
 elif kind=='density':X[:,0]=np.where(y==0,-1.,1.)+rng.normal(0,1.3,n);X[:,1:]*=1.8
 elif kind=='curved':
  angle=rng.uniform(0,np.pi,n);X[:,0]=np.where(y==0,np.cos(angle),1-np.cos(angle))+rng.normal(0,.12,n);X[:,1]=np.where(y==0,np.sin(angle),.5-np.sin(angle))+rng.normal(0,.12,n)
 elif kind!='null':raise ValueError(kind)
 pairs=min(int(noise*n/2),np.sum(y==1),np.sum(y==0))
 if pairs:
  flip=np.r_[rng.choice(np.flatnonzero(y==0),pairs,False),rng.choice(np.flatnonzero(y==1),pairs,False)];y[flip]=1-y[flip]
 X[:,0]+=offset;return X,y
def generate_split(family,n,q,mixture_weight,dimension,noise,seed):
 rng=np.random.default_rng(seed);types=FAMILIES[family];counts=_counts(n,len(types),mixture_weight);Xs=[];ys=[];regions=[];centers=[]
 for i,(kind,count) in enumerate(zip(types,counts)):
  X,y=_region(kind,int(count),q,dimension,noise,rng,offset=8*i);Xs.append(X);ys.append(y);regions.append(np.full(len(y),i));centers.append(X.mean(0))
 order=rng.permutation(sum(counts));return np.vstack(Xs)[order],np.concatenate(ys)[order],np.concatenate(regions)[order],np.vstack(centers)
def generate_dataset(params,seed):
 n=int(params['n']);common=(params['family'],float(params['q']),float(params['mixture_weight']),int(params['dimension']),float(params['noise']));train=generate_split(common[0],n,*common[1:],seed*11+1);val=generate_split(common[0],max(300,n//2),*common[1:],seed*11+2);test=generate_split(common[0],max(1000,n),*common[1:],seed*11+3);return train,val,test,{'region_types':FAMILIES[params['family']]}
