"""Aggregate v2 risk-resource frontiers and apply Theory-3 gates."""
import collections,csv,json,statistics
import numpy as np
from scipy.stats import spearmanr
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def marginal_stats(frontier):
 vals=[];region_vals=collections.defaultdict(list)
 ordered=sorted(frontier,key=lambda x:(x['cost'],x['risk']))
 for a,b in zip(ordered,ordered[1:]):
  dc=b['cost']-a['cost'];dr=a['risk']-b['risk']
  if dc<=0 or dr<0:continue
  v=dr/dc;vals.append(v)
  for j,(x,y) in enumerate(zip(a.get('taus',[]),b.get('taus',[]))):
   if x!=y:region_vals[j].append(v)
 n_regions=len(ordered[0].get('taus',[])) if ordered else 0;scores=[statistics.mean(region_vals[j]) if region_vals[j] else 0 for j in range(n_regions)]
 return {'event_values':vals,'mean':statistics.mean(vals) if vals else 0,'variance':statistics.pvariance(vals) if len(vals)>1 else 0,'region_scores':scores,'region_score_variance':statistics.pvariance(scores) if len(scores)>1 else 0}
def classify(r):
 a=r['additional_metrics'];global_=a['global_frontier'];oracle=a['oracle_frontier'];cond_a=any(abs(o['risk']-g['risk'])<=.005 and o['cost']<=.7*g['cost'] for g in global_ for o in oracle);cond_b=any(o['cost']<=g['cost'] and o['risk']<=g['risk']-.01 for g in global_ for o in oracle);regrets=[g['frontier_regret'] or 0 for g in global_];p=next(x for x in a['risk_budget_points'] if abs(x['epsilon']-.01)<1e-12);same=[g for g in global_ if g['risk']<=p['risk']+.005];estimated_a=bool(same) and p['cost']<=.7*min(g['cost'] for g in same);mv=marginal_stats(oracle);return {'experiment_id':r['experiment_id'],'base_config':r['dataset_generation_parameters']['base_config'],'family':r['dataset'].rsplit('-',1)[-1],'method':a.get('generation_method','kmeans'),'condition_a_oracle':cond_a,'condition_b_oracle':cond_b,'positive_global_regret':max(regrets)>1e-12,'positive_global_point_fraction':sum(x>1e-12 for x in regrets)/len(regrets),'mean_global_regret':statistics.mean(regrets),'max_global_regret':max(regrets),'estimated_eps01_oracle_regret':p['frontier_regret'] or 0,'estimated_eps01_condition_a_vs_global':estimated_a,'estimated_eps01_cost':p['cost'],'estimated_eps01_risk':p['risk'],'marginal_value_mean':mv['mean'],'marginal_value_variance':mv['variance'],'region_value_variance':mv['region_score_variance'],'region_scores_json':json.dumps(mv['region_scores'])}
def main():
 rs=[r for r in map(json.loads,(ROOT/'experiments/results/experiments.jsonl').open()) if r.get('study')=='risk-granularity-v2'];rows=[classify(r) for r in rs];out=ROOT/'experiments/results/v2_theory_frontier_rows.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 groups=collections.defaultdict(list)
 for r in rows:groups[r['method'],r['family']].append(r)
 summary=[]
 for (m,f),x in sorted(groups.items()):summary.append({'method':m,'family':f,'runs':len(x),'oracle_condition_a_fraction':statistics.mean(r['condition_a_oracle'] for r in x),'oracle_condition_b_fraction':statistics.mean(r['condition_b_oracle'] for r in x),'positive_regret_run_fraction':statistics.mean(r['positive_global_regret'] for r in x),'mean_global_regret':statistics.mean(r['mean_global_regret'] for r in x),'estimated_eps01_mean_oracle_regret':statistics.mean(r['estimated_eps01_oracle_regret'] for r in x),'estimated_eps01_condition_a_fraction':statistics.mean(r['estimated_eps01_condition_a_vs_global'] for r in x)})
 rank_stability=[]
 grouped=collections.defaultdict(list)
 for r in rows:grouped[r['method'],r['base_config']].append(r)
 for (method,base),x in grouped.items():
  vectors=[json.loads(r['region_scores_json']) for r in x];cors=[]
  for i in range(len(vectors)):
   for j in range(i+1,len(vectors)):
    if len(vectors[i])>1 and np.ptp(vectors[i])>1e-12 and np.ptp(vectors[j])>1e-12:
     value=float(spearmanr(vectors[i],vectors[j]).statistic)
     if np.isfinite(value):cors.append(value)
  rank_stability.append({'method':method,'base_config':base,'mean_seed_rank_spearman':statistics.mean(cors) if cors else None})
 decision={'theory3_condition_c_pass':all(r['positive_regret_run_fraction']>=.8 for r in summary),'families_passed':sorted({r['family'] for r in summary if r['positive_regret_run_fraction']>=.8}),'methods':sorted({r['method'] for r in summary}),'status':'P1_APPLICATION_EXPLANATION','collision_risk':'HIGH_STANDALONE','estimated_mechanism_note':'epsilon=.01 test-risk regret is small, but >=30% resource savings is not stable across all families/methods','marginal_value_mean_variance':statistics.mean(r['marginal_value_variance'] for r in rows),'region_value_mean_variance':statistics.mean(r['region_value_variance'] for r in rows),'mean_seed_rank_spearman':statistics.mean(r['mean_seed_rank_spearman'] for r in rank_stability if r['mean_seed_rank_spearman'] is not None)}
 (ROOT/'experiments/results/v2_theory_frontier_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');(ROOT/'experiments/results/v2_theory_gate_decision.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n');(ROOT/'experiments/results/v2_marginal_value_rank_stability.json').write_text(json.dumps(rank_stability,indent=2,sort_keys=True)+'\n');print(json.dumps({'summary':summary,'decision':decision},indent=2));return rows,summary
if __name__=='__main__':main()
