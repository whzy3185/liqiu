"""Communication-budgeted federated prototype benchmark on sklearn Digits."""
import math,time,warnings
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,f1_score,log_loss
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from studies.risk_granularity.frontier import pareto_front,frontier_regret
from studies.risk_granularity.tree import GranulationTree
THRESHOLDS=(.55,.60,.65,.70,.75,.80,.85,.90,.95,1.0);MODELS=('nearest','logistic','mlp')
def client_probabilities(classes,m,alpha,rng):
 scale=np.linspace(1,5,m);rng.shuffle(scale);p=[]
 for _ in classes:
  x=rng.dirichlet(np.full(m,alpha))*scale;p.append(x/x.sum())
 return np.asarray(p),scale
def assign(y,probs,rng,ensure=False):
 out=np.empty(len(y),int)
 for c in np.unique(y):
  idx=np.flatnonzero(y==c);out[idx]=rng.choice(probs.shape[1],len(idx),p=probs[int(c)])
 if ensure:
  for client in range(probs.shape[1]):
   if not np.any(out==client):
    donor=max(range(probs.shape[1]),key=lambda j:np.sum(out==j));idx=np.flatnonzero(out==donor)[0];out[idx]=client
 return out
def entropy(y):
 c=np.bincount(y,minlength=10);p=c[c>0]/c.sum();return float(-np.sum(p*np.log(p)))
def options_for_client(X,y,seed):
 tree=GranulationTree(random_state=101+seed).fit(X,y);opts=[];seen=set()
 for tau in THRESHOLDS:
  leaves=tree.cut(tau);centers=np.vstack([n.center for n in leaves]);labels=np.array([n.label for n in leaves]);weights=np.array([len(n.indices) for n in leaves],float);soft=np.vstack([np.bincount(y[n.indices],minlength=10)/len(n.indices) for n in leaves]);key=tuple(sorted(tuple(x) for x in [n.indices.tolist() for n in leaves]))
  if key in seen:continue
  seen.add(key);opts.append({'tau':tau,'cost':len(leaves),'centers':centers,'labels':labels,'weights':weights,'soft':soft})
 return opts
def proto_bytes(k,d):return int(k*(d+10+1)*4)
def merge_options(options,selection):
 chosen=[options[i][j] for i,j in enumerate(selection)];return np.vstack([x['centers'] for x in chosen]),np.concatenate([x['labels'] for x in chosen]),np.concatenate([x['weights'] for x in chosen]),np.vstack([x['soft'] for x in chosen]),sum(x['cost'] for x in chosen)
def nearest_prob(centers,soft,X):return soft[np.argmin(np.linalg.norm(X[:,None,:]-centers[None,:,:],axis=2),axis=1)]
def expand_prob(model,X):
 raw=model.predict_proba(X);out=np.zeros((len(X),10));out[:,model.classes_.astype(int)]=raw;return out
def evaluate_server(options,selection,X,y,client_ids,model_name,seed):
 centers,labels,weights,soft,k=merge_options(options,selection)
 if model_name=='nearest':prob=nearest_prob(centers,soft,X)
 elif model_name=='logistic':
  model=LogisticRegression(max_iter=250,random_state=seed).fit(centers,labels,sample_weight=weights);prob=expand_prob(model,X)
 elif model_name=='mlp':
  with warnings.catch_warnings():warnings.simplefilter('ignore');model=MLPClassifier(hidden_layer_sizes=(16,),solver='lbfgs',max_iter=80,random_state=seed).fit(centers,labels);prob=expand_prob(model,X)
 else:raise ValueError(model_name)
 pred=np.argmax(prob,axis=1);client_acc=[accuracy_score(y[client_ids==i],pred[client_ids==i]) for i in np.unique(client_ids) if np.any(client_ids==i)];return {'accuracy':float(accuracy_score(y,pred)),'macro_f1':float(f1_score(y,pred,average='macro',zero_division=0)),'nll':float(log_loss(y,np.clip(prob,1e-9,1),labels=np.arange(10))),'brier':float(np.mean(np.sum((prob-np.eye(10)[y])**2,axis=1))),'worst_client_accuracy':float(min(client_acc)),'prototype_count':k}
def local_risk(option,X,y):
 if len(y)==0:return .5
 return 1-accuracy_score(y,np.argmax(nearest_prob(option['centers'],option['soft'],X),axis=1))
def transition_values(options,X,y,d):
 values=[]
 for client,opts in enumerate(options):
  local=[]
  for j in range(len(opts)-1):
   gain=local_risk(opts[j],X[client],y[client])-local_risk(opts[j+1],X[client],y[client]);delta=proto_bytes(opts[j+1]['cost']-opts[j]['cost'],d);local.append(gain/delta if delta>0 else 0)
  values.append(local)
 return values
def allocate_greedy(options,values,budget,d):
 selection=[0]*len(options);steps=[];cost=proto_bytes(sum(x[0]['cost'] for x in options),d)
 while True:
  candidates=[]
  for i,opts in enumerate(options):
   j=selection[i]
   if j+1<len(opts):
    delta=proto_bytes(opts[j+1]['cost']-opts[j]['cost'],d)
    if cost+delta<=budget:candidates.append((values[i][j],-delta,-i,i,delta))
  if not candidates:break
  value,_,_,client,delta=max(candidates);selection[client]+=1;cost+=delta;steps.append({'client':client,'value':value,'delta_bytes':delta,'cost_after':cost})
 return selection,steps
def budget_selection(options,budget,weights,d,mode):
 minimum=[x[0]['cost'] for x in options];remaining=max(0,budget-proto_bytes(sum(minimum),d));units=remaining/((d+11)*4);alloc=np.full(len(options),units/len(options)) if mode=='equal' else units*weights/weights.sum();selection=[]
 for i,opts in enumerate(options):
  cap=minimum[i]+alloc[i];selection.append(max((j for j,o in enumerate(opts) if o['cost']<=cap),default=0))
 return selection
def coordinate_oracle(options,budget,d,starts,X,y):
 cache={}
 def risk(selection):
  key=tuple(selection)
  if key not in cache:
   centers,_,_,soft,_=merge_options(options,selection);cache[key]=local_risk({'centers':centers,'soft':soft},X,y)
  return cache[key]
 best=None
 for start in starts:
  selection=list(start)
  if proto_bytes(sum(options[i][j]['cost'] for i,j in enumerate(selection)),d)>budget:continue
  current=risk(selection)
  for _ in range(3):
   changed=False
   for i,opts in enumerate(options):
    candidate=(current,selection[i])
    for j in range(len(opts)):
     trial=selection.copy();trial[i]=j
     if proto_bytes(sum(options[k][v]['cost'] for k,v in enumerate(trial)),d)>budget:continue
     value=risk(trial)
     if value<candidate[0]-1e-12 or (abs(value-candidate[0])<=1e-12 and opts[j]['cost']<opts[candidate[1]]['cost']):candidate=(value,j)
    if candidate[1]!=selection[i]:selection[i]=candidate[1];current=candidate[0];changed=True
   if not changed:break
  item=(current,proto_bytes(sum(options[i][j]['cost'] for i,j in enumerate(selection)),d),selection)
  if best is None or item[:2]<best[:2]:best=item
 return best[2],{'test_risk':best[0],'evaluated_selections':len(cache)}
def evaluate_federated_digits(params,seed):
 start=time.perf_counter();digits=load_digits();X=digits.data.astype(float)/16;y=digits.target;Xtrain,Xtmp,ytrain,ytmp=train_test_split(X,y,test_size=.4,stratify=y,random_state=seed);Xval,Xtest,yval,ytest=train_test_split(Xtmp,ytmp,test_size=.5,stratify=ytmp,random_state=seed);rng=np.random.default_rng(seed);m=int(params['clients']);probs,quantity_scale=client_probabilities(np.arange(10),m,float(params['alpha']),rng);ctr=assign(ytrain,probs,rng,True);cval=assign(yval,probs,rng);ctest=assign(ytest,probs,rng);options=[];clients=[]
 for i in range(m):
  Xi=Xtrain[ctr==i];yi=ytrain[ctr==i];opts=options_for_client(Xi,yi,seed+i);options.append(opts);difficulty=0.0
  if len(np.unique(yi))>1 and len(yi)>=15:
   counts=np.bincount(yi);positive=counts[counts>0];cv=min(3,int(positive.min()))
   if cv>=2:difficulty=float(1-np.mean(cross_val_score(KNeighborsClassifier(3),Xi,yi,cv=cv)))
  clients.append({'client':i,'sample_count':len(yi),'label_entropy':entropy(yi),'local_difficulty':difficulty,'granule_counts':[o['cost'] for o in opts],'quantity_scale':float(quantity_scale[i])})
 d=X.shape[1];min_count=sum(o[0]['cost'] for o in options);max_count=sum(o[-1]['cost'] for o in options);budget_fracs=(0,.25,.5,.75,1.0);budgets=[proto_bytes(int(round(min_count+f*(max_count-min_count))),d) for f in budget_fracs];val_by=[[Xval[cval==i] for i in range(m)],[yval[cval==i] for i in range(m)]];estimated_values=transition_values(options,*val_by,d);points=[];cache={};estimated_step_values=[];uniform_selections=[]
 def add(method,selection,budget_label,steps=None):
  key=tuple(selection)
  for model_name in MODELS:
   ck=(key,model_name)
   if ck not in cache:cache[ck]=evaluate_server(options,selection,Xtest,ytest,ctest,model_name,seed)
   metrics=cache[ck];bytes_=proto_bytes(metrics['prototype_count'],d);values=[s['value'] for s in (steps or [])];points.append({'method':method,'server_model':model_name,'budget_target_bytes':budget_label,'cost':bytes_,'risk':1-metrics['accuracy'],**metrics,'selection':list(selection),'allocation_step_count':len(values),'allocation_value_mean':float(np.mean(values)) if values else None,'allocation_value_variance':float(np.var(values)) if values else None})
 for j,tau in enumerate(THRESHOLDS):
  selection=[max((k for k,o in enumerate(opts) if o['tau']<=tau),default=0) for opts in options];uniform_selections.append(selection);add('uniform_tau',selection,tau)
 for budget in budgets:
  equal=budget_selection(options,budget,np.ones(m),d,'equal');prop=budget_selection(options,budget,np.array([c['sample_count'] for c in clients]),d,'proportional');sel,steps=allocate_greedy(options,estimated_values,budget,d);estimated_step_values.extend(s['value'] for s in steps);add('equal_budget',equal,budget);add('proportional_budget',prop,budget);add('risk_value_estimated',sel,budget,steps);starts=[equal,prop,sel]+[u for u in uniform_selections if proto_bytes(sum(options[i][j]['cost'] for i,j in enumerate(u)),d)<=budget];oracle_sel,oracle_diag=coordinate_oracle(options,budget,d,starts,Xtest,ytest);add('client_oracle_coordinate',oracle_sel,budget,[{'client':-1,'value':-oracle_diag['test_risk'],'delta_bytes':0,'evaluated_selections':oracle_diag['evaluated_selections']}])
 # Central full-data upper controls; communication is counted as sending every example plus metadata.
 full_soft=np.eye(10)[ytrain];full_opts=[[{'tau':1.,'cost':len(ytrain),'centers':Xtrain,'labels':ytrain,'weights':np.ones(len(ytrain)),'soft':full_soft}]]
 old=options;options=full_opts
 for model_name in MODELS:
  met=evaluate_server(options,[0],Xtest,ytest,ctest,model_name,seed);points.append({'method':'full_central','server_model':model_name,'budget_target_bytes':proto_bytes(len(ytrain),d),'cost':proto_bytes(len(ytrain),d),'risk':1-met['accuracy'],**met,'selection':[0],'allocation_steps':[]})
 options=old;frontier=pareto_front(points);all_regret=frontier_regret(points,frontier);uniform=[p for p in all_regret if p['method']=='uniform_tau'];oracle=[p for p in points if p['method']=='client_oracle_coordinate'];estimated=[p for p in points if p['method']=='risk_value_estimated'];uniform_gap=[p['frontier_regret'] for p in uniform if p['frontier_regret'] is not None];uniform_oracle_gap=[];estimated_gap=[]
 raw_uniform=[p for p in points if p['method']=='uniform_tau']
 for p in uniform:
  same=[o for o in oracle+raw_uniform if o['server_model']==p['server_model'] and o['cost']<=p['cost']]
  if same:uniform_oracle_gap.append(p['risk']-min(o['risk'] for o in same))
 for p in estimated:
  same=[o for o in oracle+[p] if o['server_model']==p['server_model'] and o['cost']<=p['cost']]
  if same:estimated_gap.append(p['risk']-min(o['risk'] for o in same))
 primary=min((p for p in points if p['method']=='risk_value_estimated' and p['server_model']=='nearest'),key=lambda p:abs(p['budget_target_bytes']-budgets[len(budgets)//2]));value_samples=estimated_step_values
 nearest_estimated_gap=[]
 for p in estimated:
  if p['server_model']!='nearest':continue
  same=[o for o in oracle+[p] if o['server_model']=='nearest' and o['cost']<=p['cost']]
  if same:nearest_estimated_gap.append(p['risk']-min(o['risk'] for o in same))
 return {'accuracy':primary['accuracy'],'macro_f1':primary['macro_f1'],'nll':primary['nll'],'brier':primary['brier'],'prototype_count':primary['prototype_count'],'bytes':primary['cost'],'runtime':time.perf_counter()-start,'points':points,'frontier':frontier,'clients':clients,'budgets':budgets,'uniform_to_best_mean_regret':float(np.mean(uniform_gap)),'uniform_to_best_max_regret':float(np.max(uniform_gap)),'uniform_to_oracle_mean_regret':float(np.mean(uniform_oracle_gap)) if uniform_oracle_gap else None,'estimated_to_oracle_mean_regret':float(np.mean(estimated_gap)) if estimated_gap else None,'estimated_to_oracle_nearest_mean_regret':float(np.mean(nearest_estimated_gap)) if nearest_estimated_gap else None,'marginal_value_variance':float(np.var(value_samples)) if value_samples else 0,'marginal_value_count':len(value_samples),'min_prototypes':min_count,'max_prototypes':max_count}
