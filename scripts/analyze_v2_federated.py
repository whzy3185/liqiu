"""Aggregate FED Digits risk/communication frontiers and apply kill gates."""
import collections,csv,json,statistics
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[r for r in map(json.loads,(ROOT/'experiments/results/experiments.jsonl').open()) if r.get('study')=='federated-risk-granularity-v2']
 if len(rs)!=60:raise SystemExit(f'expected 60 got {len(rs)}')
 run_rows=[];point_rows=[]
 for r in rs:
  p=r['dataset_generation_parameters'];run_rows.append({'experiment_id':r['experiment_id'],'clients':p['clients'],'alpha':p['alpha'],'seed':r['seed'],'uniform_to_oracle_regret':r['additional_metrics']['uniform_to_observed_oracle_mean_regret'],'estimated_to_oracle_nearest_regret':r['additional_metrics']['estimated_to_observed_oracle_nearest_mean_regret'],'marginal_value_variance':r['additional_metrics']['marginal_value_variance']})
  pts=r['additional_metrics']['frontier_points']
  for model in ('nearest','logistic','mlp'):
   est=[x for x in pts if x['method']=='risk_value_estimated' and x['server_model']==model];base=[x for x in pts if x['method'] in ('uniform_tau','equal_budget','proportional_budget') and x['server_model']==model]
   for x in est:
    feasible=[b for b in base if b['cost']<=x['cost']];best=min(feasible,key=lambda z:z['risk']) if feasible else None;same=[b for b in base if b['risk']<=x['risk']+.003];point_rows.append({'experiment_id':r['experiment_id'],'clients':p['clients'],'alpha':p['alpha'],'seed':r['seed'],'server_model':model,'budget_target':x['budget_target_bytes'],'bytes':x['cost'],'accuracy':x['accuracy'],'worst_client_accuracy':x['worst_client_accuracy'],'accuracy_advantage_same_cost':None if best is None else best['risk']-x['risk'],'worst_client_advantage_same_cost':None if best is None else x['worst_client_accuracy']-best['worst_client_accuracy'],'resource_ratio_same_accuracy':None if not same else x['cost']/min(b['cost'] for b in same)})
 for name,rows in [('runs',run_rows),('points',point_rows)]:
  with (ROOT/f'experiments/results/v2_federated_{name}.csv').open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 model_summary=[]
 for model in ('nearest','logistic','mlp'):
  x=[r for r in point_rows if r['server_model']==model];adv=[r['accuracy_advantage_same_cost'] for r in x if r['accuracy_advantage_same_cost'] is not None];worst=[r['worst_client_advantage_same_cost'] for r in x if r['worst_client_advantage_same_cost'] is not None];ratio=[r['resource_ratio_same_accuracy'] for r in x if r['resource_ratio_same_accuracy'] is not None];model_summary.append({'server_model':model,'points':len(x),'mean_accuracy_advantage_same_cost':statistics.mean(adv),'condition_a_point_fraction':float(np.mean(np.array(adv)>=.005)),'mean_worst_client_advantage':statistics.mean(worst),'condition_c_point_fraction':float(np.mean(np.array(worst)>=.01)),'median_resource_ratio_same_accuracy':statistics.median(ratio),'condition_b_point_fraction':float(np.mean(np.array(ratio)<=.8))})
 alpha_summary=[]
 for alpha in (.05,.1,.3,1.0):
  x=[r for r in run_rows if r['alpha']==alpha];alpha_summary.append({'alpha':alpha,'runs':len(x),'uniform_to_oracle_mean_regret':statistics.mean(r['uniform_to_oracle_regret'] for r in x),'estimated_to_oracle_nearest_mean_regret':statistics.mean(r['estimated_to_oracle_nearest_regret'] for r in x)})
 decision={'status':'P1_PROBLEM_METHOD_REJECTED','uniform_to_observed_oracle_mean_regret':statistics.mean(r['uniform_to_oracle_regret'] for r in run_rows),'estimated_to_observed_oracle_nearest_mean_regret':statistics.mean(r['estimated_to_oracle_nearest_regret'] for r in run_rows),'uniform_gap_positive_run_fraction':float(np.mean([r['uniform_to_oracle_regret']>1e-12 for r in run_rows])),'mean_marginal_value_variance':statistics.mean(r['marginal_value_variance'] for r in run_rows),'model_summary':model_summary,'alpha_summary':alpha_summary,'continue_to_mnist_fashion':False,'reason':'F5 does not beat uniform/equal/proportional at equal bytes and does not close the observed-oracle gap on Digits.'}
 (ROOT/'experiments/results/v2_federated_gate_decision.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n');print(json.dumps(decision,indent=2));return decision
if __name__=='__main__':main()
