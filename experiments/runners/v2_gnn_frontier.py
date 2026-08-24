"""CPU sparse-GCN risk-compression frontier runner."""
import time
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from sklearn.metrics import f1_score,log_loss
from studies.graph_coarsening import *
ROOT=Path(__file__).resolve().parents[2]
def run(config:Mapping[str,Any]):
 seed=int(config['seed']);p=config['dataset_generation_parameters'];data=load_planetoid(ROOT/'work/planetoid',p['dataset']);n=data['features'].shape[0];method=config['hyperparameters']['method'];ratio=config['hyperparameters'].get('ratio',1.);start=time.perf_counter();deviation=[]
 if method=='full':assignment=identity_assignment(n);meta={'mode':'full'}
 elif method=='random':assignment=random_assignment(n,max(1,int(round(n*ratio))),seed);meta={'mode':'random'}
 elif method=='heavy_edge':assignment=heavy_edge_assignment(data['adjacency'],max(1,int(round(n*ratio))),seed);meta={'mode':'heavy_edge_matching'}
 elif method=='gbgc_adaptive':assignment,meta=gbgc_adaptive_assignment(data['adjacency']);deviation=meta['paper_deviations']
 elif method=='gbgc_fixed':assignment,meta=gbgc_fixed_ratio_assignment(data['adjacency'],ratio);deviation=meta['paper_deviations']
 else:raise ValueError(method)
 preprocessing=time.perf_counter()-start;coarse=coarsen_graph(data['features'],data['adjacency'],data['labels'],data['train_idx'],assignment);result=train_gcn(coarse['features'],coarse['adjacency'],coarse['train_groups'],coarse['train_labels'],assignment,data['labels'],data['val_idx'],data['test_idx'],seed,epochs=100,patience=20);prob=result['probabilities'][data['test_idx']];pred=result['predictions'][data['test_idx']];y=data['labels'][data['test_idx']];retained=coarse['features'].shape[0];edges=coarse['adjacency'].nnz//2
 return {'metrics':{'accuracy':result['accuracy'],'macro_f1':float(f1_score(y,pred,average='macro')),'auroc':None,'calibration_error':None,'additional':{'nll':float(log_loss(y,np.clip(prob,1e-9,1),labels=np.arange(prob.shape[1]))),'retained_nodes':retained,'retained_edges':edges,'retained_node_ratio':retained/n,'preprocessing_seconds':preprocessing,'training_seconds':result['training_seconds'],'epochs':result['epochs'],'python_peak_memory_bytes':result['python_peak_memory_bytes'],'tensor_memory_bytes':result['tensor_memory_bytes'],'cleanroom_deviations':deviation,'coarsening_meta':meta}},'structure':{'granule_count':retained,'average_granule_size':float(np.mean(coarse['counts'])),'uncertain_sample_ratio':None,'additional':{'compression_ratio':retained/n,'retained_edges':edges}},'outcome':'success','notes':'V2 CPU GCN frontier. GBGC rows are disclosed clean-room paper-spec implementations, not author-code reproduction.'}
