"""Deterministic batch streams with explicit drift ground truth."""
import numpy as np
STREAM_KINDS=('covariate_shift','concept_drift','prior_shift','density_drift','emerging_class','disappearing_class')
def generate_stream(kind,n_steps=10,samples_per_step=200,seed=42,ambient_dimension=2,drift_strength=2.0):
 if kind not in STREAM_KINDS:raise ValueError(kind)
 if n_steps<2 or samples_per_step<10 or ambient_dimension<2:raise ValueError('n_steps>=2, samples_per_step>=10, ambient_dimension>=2')
 rng=np.random.default_rng(seed);projection=rng.normal(size=(2,ambient_dimension))/np.sqrt(2);Xs=[];ys=[];ts=[];params=[]
 for step in range(n_steps):
  u=step/(n_steps-1);n=samples_per_step
  if kind=='concept_drift':
   X=rng.uniform(-1,1,(n,2));angle=drift_strength*np.pi*u/2;normal=np.array([np.cos(angle),np.sin(angle)]);y=(X@normal>=0).astype(int);info={'angle':angle}
  else:
   if kind=='prior_shift':prior=.1+.8*u
   elif kind=='disappearing_class':prior=.5*(1-u)
   else:prior=.5
   y=(rng.random(n)<prior).astype(int);means=np.array([[-1.,0.],[1.,0.]])
   if kind=='covariate_shift':means=means+np.array([drift_strength*(u-.5),0])
   std=.25+(drift_strength*.35*u if kind=='density_drift' else 0);X=means[y]+rng.normal(0,std,(n,2));info={'class1_prior':prior,'std':std,'translation':means.mean(0).tolist()}
   if kind=='emerging_class' and step>=n_steps//2:
    emerge=(rng.random(n)<.4*(u-.5)/.5);y[emerge]=2;X[emerge]=np.array([0.,1.8])+rng.normal(0,.25,(emerge.sum(),2));info['emerging_fraction']=float(emerge.mean())
  X=X@projection if ambient_dimension>2 else X;Xs.append(X);ys.append(y);ts.append(np.full(n,step));params.append(info)
 return np.vstack(Xs).astype(float),np.concatenate(ys).astype(int),np.concatenate(ts).astype(int),{'kind':kind,'seed':seed,'n_steps':n_steps,'samples_per_step':samples_per_step,'ambient_dimension':ambient_dimension,'drift_strength':drift_strength,'step_parameters':params}
