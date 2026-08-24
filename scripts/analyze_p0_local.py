"""Aggregate P0 stable local-pruning cheap test and sensitivity."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"p0lv1-' in x or '"p0lv2-' in x]
 if len(rs)!=45:raise SystemExit(f'expected 45 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:
  setting=('min'+str(r['hyperparameters']['min_validation'])+'_cost'+str(r['hyperparameters']['cost_per_leaf']));g[r['dataset'],setting].append(r)
 rows=[]
 for (d,s),x in sorted(g.items()):rows.append({'dataset':d,'setting':s,'runs':len(x),'mean_accuracy_delta':statistics.mean(r['additional_metrics']['accuracy_delta'] for r in x),'max_accuracy_delta':max(r['additional_metrics']['accuracy_delta'] for r in x),'mean_brier_delta':statistics.mean(r['additional_metrics']['brier_delta'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x),'mean_baseline_granules':statistics.mean(statistics.mean(r['additional_metrics']['baseline_fold_granules']) for r in x)})
 out=ROOT/'experiments/results/p0_local_v1_v2_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
