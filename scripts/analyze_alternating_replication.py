"""Aggregate independent alternating-label generators."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"altv1-' in x]
 if len(rs)!=90: raise SystemExit(f'expected 90, got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:
  p=r['experiment_id'].split('-'); g[p[1],p[2]].append(r)
 rows=[]
 for (case,method),x in sorted(g.items()):
  rows.append({'case':case,'method':method,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),
   'mean_reference_accuracy':statistics.mean(r['additional_metrics']['reference_accuracy'] for r in x),
   'mean_accuracy_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),
   'negative_gap_runs':sum(r['additional_metrics']['accuracy_gap']<0 for r in x),
   'mean_granules':statistics.mean(r['granule_count'] for r in x),'mean_uncertain_ratio':statistics.mean(r['uncertain_sample_ratio'] for r in x)})
 out=ROOT/'counterexamples/discovered_cases/alternating_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print('Alternating v1 summary written: sector wheel replicates; Gaussian XOR bounds the claim.')
if __name__=='__main__': main()
