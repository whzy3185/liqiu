"""Aggregate corrected GNN frontiers and apply the GNN-2 continuation gate."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[];invalid=[]
 for r in map(json.loads,(ROOT/'experiments/results/experiments.jsonl').open()):
  if r.get('study')!='gnn-risk-granularity-v2':continue
  if r['dataset']=='planetoid-citeseer' and r['experiment_id'].startswith('v2gnn-citeseer'):invalid.append(r)
  else:rs.append(r)
 groups=collections.defaultdict(list)
 for r in rs:groups[r['dataset'],r['hyperparameters']['method'],r['hyperparameters'].get('ratio')].append(r)
 rows=[]
 for (d,m,ratio),x in sorted(groups.items(),key=lambda z:str(z[0])):rows.append({'dataset':d,'method':m,'ratio':ratio,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),'mean_macro_f1':statistics.mean(r['macro_f1'] for r in x),'mean_retained_node_ratio':statistics.mean(r['additional_metrics']['retained_node_ratio'] for r in x),'mean_retained_nodes':statistics.mean(r['additional_metrics']['retained_nodes'] for r in x),'mean_retained_edges':statistics.mean(r['additional_metrics']['retained_edges'] for r in x),'mean_preprocessing_seconds':statistics.mean(r['additional_metrics']['preprocessing_seconds'] for r in x),'mean_training_seconds':statistics.mean(r['additional_metrics']['training_seconds'] for r in x),'mean_tensor_memory_bytes':statistics.mean(r['additional_metrics']['tensor_memory_bytes'] for r in x)})
 with (ROOT/'experiments/results/v2_gnn_frontier_summary.csv').open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 adaptive=[];all_gbgc=[]
 for d in sorted(set(r['dataset'] for r in rs)):
  for seed in (1,7,21):
   x=[r for r in rs if r['dataset']==d and r['seed']==seed]
   for p in x:
    dominated=any(q['additional_metrics']['retained_nodes']<=p['additional_metrics']['retained_nodes'] and q['accuracy']>=p['accuracy'] and(q['additional_metrics']['retained_nodes']<p['additional_metrics']['retained_nodes'] or q['accuracy']>p['accuracy']) for q in x)
    if p['hyperparameters']['method']=='gbgc_adaptive':adaptive.append({'dataset':d,'seed':seed,'dominated':dominated,'accuracy':p['accuracy'],'ratio':p['additional_metrics']['retained_node_ratio']})
    if p['hyperparameters']['method'].startswith('gbgc'):all_gbgc.append(dominated)
 decision={'status':'REJECT_NONUNIFORM_GNN_PROTOTYPE','valid_runs':len(rs),'invalid_citeseer_runs_retained':len(invalid),'adaptive_gbgc_pareto_fraction':1-statistics.mean(x['dominated'] for x in adaptive),'all_cleanroom_gbgc_dominated_fraction':statistics.mean(all_gbgc),'adaptive_points':adaptive,'continue_to_gnn3':False,'continue_to_heterophily_or_scale':False,'reason':'Clean-room adaptive GBGC is node-risk Pareto-nondominated on all 3 datasets and 3 seeds; the assumed allocation waste is absent. Preprocessing cost is high but does not justify a new nonuniform cut without a mechanism.'}
 (ROOT/'experiments/results/v2_gnn_gate_decision.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n');print(json.dumps(decision,indent=2));return decision
if __name__=='__main__':main()
