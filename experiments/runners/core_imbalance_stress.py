from typing import Any,Mapping
import numpy as np
from counterexamples.generators import generate
from studies.granular_ball_core import fit_tree_frontier,reference_metrics
def data(family,n,ratio,seed,balanced=False):
 target=1 if balanced else ratio
 if family=='density_equal':return generate('imbalanced_density',n_samples=n,seed=seed,imbalance_ratio=target,density_ratio=1,manifold_width=.18)[:2]
 if family=='density_shift':return generate('imbalanced_density',n_samples=n,seed=seed,imbalance_ratio=target,density_ratio=10,manifold_width=.25)[:2]
 X,y,_=generate('moons',n_samples=n*2 if not balanced else n,seed=seed,manifold_width=.14)
 if balanced:return X,y
 rng=np.random.default_rng(seed);major=np.flatnonzero(y==0);minor=np.flatnonzero(y==1);keep_minor=rng.choice(minor,max(2,len(major)//int(ratio)),False);idx=np.r_[major,keep_minor];rng.shuffle(idx);return X[idx],y[idx]
def run(config:Mapping[str,Any]):
 p=config['dataset_generation_parameters'];seed=int(config['seed']);X,y=data(p['family'],600,int(p['imbalance_ratio']),seed);Xt,yt=data(p['family'],1200,1,seed+10000,True);frontier=fit_tree_frontier(X,y,Xt,yt,p['generation_method'],seed);refs=reference_metrics(X,y,Xt,yt,seed);primary=next(x for x in frontier if x['tau']==.85);best_ref=max(v['macro_f1'] for v in refs.values())
 return {'metrics':{'accuracy':primary['accuracy'],'macro_f1':primary['macro_f1'],'auroc':None,'calibration_error':primary['ece'],'additional':{'frontier':frontier,'references':refs,'best_reference_macro_f1':best_ref,'macro_f1_gap':primary['macro_f1']-best_ref,'train_class_counts':np.bincount(y,minlength=2).tolist()}},'structure':{'granule_count':primary['granules'],'average_granule_size':primary['mean_size'],'uncertain_sample_ratio':None,'additional':{'fragmentation_ratio':primary['fragmentation_ratio'],'mean_purity':primary['mean_purity']}},'outcome':'success','notes':'GB-only imbalance/minority masking stress; test distribution is balanced.'}
