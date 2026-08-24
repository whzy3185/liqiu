"""Aggregate public OpenML exploration without causal overclaiming."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"realv1-' in x]
 if len(rs)!=25: raise SystemExit(f'expected 25, got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs: g[r['dataset']].append(r)
 rows=[]
 for dataset,x in sorted(g.items()):
  rows.append({'dataset':dataset,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),
   'std_accuracy':statistics.pstdev(r['accuracy'] for r in x),'mean_macro_f1':statistics.mean(r['macro_f1'] for r in x),
   'mean_auroc':statistics.mean(r['auroc'] for r in x),'mean_ece':statistics.mean(r['calibration_error'] for r in x),
   'mean_reference_accuracy':statistics.mean(r['additional_metrics']['reference_accuracy'] for r in x),
   'mean_accuracy_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),
   'negative_gap_runs':sum(r['additional_metrics']['accuracy_gap']<0 for r in x),
   'mean_granules':statistics.mean(r['granule_count'] for r in x),'mean_size':statistics.mean(r['average_granule_size'] for r in x),
   'mean_weighted_impurity':statistics.mean(r['structure']['weighted_impurity'] for r in x),
   'mean_low_purity_ratio':statistics.mean(r['uncertain_sample_ratio'] for r in x)})
 out=ROOT/'counterexamples/discovered_cases/real_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
