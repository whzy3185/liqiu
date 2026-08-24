"""Small sparse two-layer CPU GCN for frontier auditing."""
import time,tracemalloc
import numpy as np
import scipy.sparse as sp
import torch
def sparse_tensor(matrix):
 x=matrix.tocoo();indices=torch.tensor(np.vstack((x.row,x.col)),dtype=torch.long);values=torch.tensor(x.data,dtype=torch.float32);return torch.sparse_coo_tensor(indices,values,x.shape,check_invariants=False).coalesce()
def normalized(adj):
 a=(adj+sp.eye(adj.shape[0],dtype=np.float32)).tocoo();degree=np.asarray(a.sum(1)).ravel();d=np.power(degree,-.5,where=degree>0);return sp.diags(d)@a@sp.diags(d)
class GCN(torch.nn.Module):
 def __init__(self,din,hidden,classes,dropout):super().__init__();self.w1=torch.nn.Linear(din,hidden,bias=False);self.w2=torch.nn.Linear(hidden,classes,bias=False);self.dropout=dropout
 def forward(self,x,a):x=torch.sparse.mm(a,self.w1(x));x=torch.relu(x);x=torch.nn.functional.dropout(x,self.dropout,self.training);return torch.sparse.mm(a,self.w2(x))
def train_gcn(features,adjacency,train_groups,train_labels,assignment,labels,val_idx,test_idx,seed,epochs=120,patience=20):
 torch.manual_seed(seed);np.random.seed(seed);torch.set_num_threads(1);x=torch.tensor(features.toarray() if sp.issparse(features) else features,dtype=torch.float32);a=sparse_tensor(normalized(adjacency));idx=torch.tensor(train_groups,dtype=torch.long);y=torch.tensor(train_labels[train_groups],dtype=torch.long);model=GCN(x.shape[1],16,int(labels.max()+1),.5);opt=torch.optim.Adam(model.parameters(),lr=.01,weight_decay=5e-4);best=None;bad=0;start=time.perf_counter();tracemalloc.start()
 for epoch in range(epochs):
  model.train();opt.zero_grad();out=model(x,a);loss=torch.nn.functional.cross_entropy(out[idx],y);loss.backward();opt.step();model.eval()
  with torch.no_grad():pred=out.argmax(1).numpy()[assignment];val=float(np.mean(pred[val_idx]==labels[val_idx]))
  if best is None or val>best[0]+1e-12:best=(val,{k:v.detach().clone() for k,v in model.state_dict().items()},epoch);bad=0
  else:bad+=1
  if bad>=patience:break
 model.load_state_dict(best[1]);model.eval()
 with torch.no_grad():logits=model(x,a);prob=torch.softmax(logits,1).numpy()[assignment];pred=prob.argmax(1)
 _,peak=tracemalloc.get_traced_memory();tracemalloc.stop();runtime=time.perf_counter()-start;return {'accuracy':float(np.mean(pred[test_idx]==labels[test_idx])),'validation_accuracy':best[0],'probabilities':prob,'predictions':pred,'epochs':best[2]+1,'training_seconds':runtime,'python_peak_memory_bytes':peak,'tensor_memory_bytes':int(x.nelement()*x.element_size()+a._nnz()*(a.values().element_size()+2*a.indices().element_size()))}
