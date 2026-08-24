"""Aggregate M02 global nested-validation negative control."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"m02gv2-' in x]
 if len(rs)!=45: raise SystemExit(f'expected 45 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs: g[r['dataset'],float(r['hyperparameters']['ball_cost_lambda'])].append(r)
 rows=[]
 for (d,lam),x in sorted(g.items()): rows.append({'dataset':d,'lambda':lam,'runs':len(x),'selected_purities':';'.join(str(r['additional_metrics']['selected_purity']) for r in x),
  'mean_accuracy':statistics.mean(r['accuracy'] for r in x),'mean_delta_vs_fixed':statistics.mean(r['additional_metrics']['accuracy_delta_vs_fixed'] for r in x),
  'min_delta_vs_fixed':min(r['additional_metrics']['accuracy_delta_vs_fixed'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x),
  'mean_baseline_granules':statistics.mean(r['additional_metrics']['baseline_p085_granules'] for r in x)})
 out=ROOT/'experiments/results/m02_global_v2_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
