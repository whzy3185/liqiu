from typing import Any,Mapping
import numpy as np
from counterexamples.generators import generate_stream
from studies.granular_ball_core import fit_tree_frontier,reference_metrics
def run(config:Mapping[str,Any]):
 p=config['dataset_generation_parameters'];seed=int(config['seed']);X,y,t,meta=generate_stream(p['shift_kind'],n_steps=10,samples_per_step=300,seed=seed,ambient_dimension=5,drift_strength=2.0);train=t==0;test=t==9;frontier=fit_tree_frontier(X[train],y[train],X[test],y[test],p['generation_method'],seed);refs=reference_metrics(X[train],y[train],X[test],y[test],seed);primary=next(x for x in frontier if x['tau']==.85);rf=refs['RandomForest']
 return {'metrics':{'accuracy':primary['accuracy'],'macro_f1':primary['macro_f1'],'auroc':None,'calibration_error':primary['ece'],'additional':{'frontier':frontier,'references':refs,'rf_accuracy':rf['accuracy'],'rf_ece':rf['ece'],'ece_gap_vs_rf':primary['ece']-rf['ece'],'accuracy_gap_vs_rf':primary['accuracy']-rf['accuracy'],'shift_meta':meta['step_parameters'][-1]}},'structure':{'granule_count':primary['granules'],'average_granule_size':primary['mean_size'],'uncertain_sample_ratio':None,'additional':{'fragmentation_ratio':primary['fragmentation_ratio'],'mean_purity':primary['mean_purity']}},'outcome':'success','notes':'GB-only static train-to-final-batch shift confidence/selective-risk stress.'}
