"""Aggregate v2 risk-resource frontiers and apply Theory-3 gates."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def classify(r):
 a=r['additional_metrics'];global_=a['global_frontier'];oracle=a['oracle_frontier'];cond_a=any(abs(o['risk']-g['risk'])<=.005 and o['cost']<=.7*g['cost'] for g in global_ for o in oracle);cond_b=any(o['cost']<=g['cost'] and o['risk']<=g['risk']-.01 for g in global_ for o in oracle);regrets=[g['frontier_regret'] or 0 for g in global_];p=next(x for x in a['risk_budget_points'] if abs(x['epsilon']-.01)<1e-12);same=[g for g in global_ if g['risk']<=p['risk']+.005];estimated_a=bool(same) and p['cost']<=.7*min(g['cost'] for g in same);return {'experiment_id':r['experiment_id'],'family':r['dataset'].rsplit('-',1)[-1],'method':a.get('generation_method','kmeans'),'condition_a_oracle':cond_a,'condition_b_oracle':cond_b,'positive_global_regret':max(regrets)>1e-12,'positive_global_point_fraction':sum(x>1e-12 for x in regrets)/len(regrets),'mean_global_regret':statistics.mean(regrets),'max_global_regret':max(regrets),'estimated_eps01_oracle_regret':p['frontier_regret'] or 0,'estimated_eps01_condition_a_vs_global':estimated_a,'estimated_eps01_cost':p['cost'],'estimated_eps01_risk':p['risk']}
def main():
 rs=[r for r in map(json.loads,(ROOT/'experiments/results/experiments.jsonl').open()) if r.get('study')=='risk-granularity-v2'];rows=[classify(r) for r in rs];out=ROOT/'experiments/results/v2_theory_frontier_rows.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 groups=collections.defaultdict(list)
 for r in rows:groups[r['method'],r['family']].append(r)
 summary=[]
 for (m,f),x in sorted(groups.items()):summary.append({'method':m,'family':f,'runs':len(x),'oracle_condition_a_fraction':statistics.mean(r['condition_a_oracle'] for r in x),'oracle_condition_b_fraction':statistics.mean(r['condition_b_oracle'] for r in x),'positive_regret_run_fraction':statistics.mean(r['positive_global_regret'] for r in x),'mean_global_regret':statistics.mean(r['mean_global_regret'] for r in x),'estimated_eps01_mean_oracle_regret':statistics.mean(r['estimated_eps01_oracle_regret'] for r in x),'estimated_eps01_condition_a_fraction':statistics.mean(r['estimated_eps01_condition_a_vs_global'] for r in x)})
 (ROOT/'experiments/results/v2_theory_frontier_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2));return rows,summary
if __name__=='__main__':main()
