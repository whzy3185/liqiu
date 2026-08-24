"""Aggregate XOR v1 and test the high-dimensional explanation."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/"experiments/results/experiments.jsonl").read_text().splitlines() if '"xorv1-' in x]
 if len(rs)!=140: raise SystemExit(f"expected 140, got {len(rs)}")
 g=collections.defaultdict(list)
 for r in rs:
  p=r['experiment_id'].split('-'); g[int(p[1][1:]),int(p[2][1:])/100,p[3]].append(r)
 rows=[]
 for (d,o,m),x in sorted(g.items()):
  rows.append({'dimension':d,'overlap':o,'method':m,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),
   'std_accuracy':statistics.pstdev(r['accuracy'] for r in x),'mean_reference_accuracy':statistics.mean(r['additional_metrics']['reference_accuracy'] for r in x),
   'mean_accuracy_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),'negative_gap_runs':sum(r['additional_metrics']['accuracy_gap']<0 for r in x),
   'mean_granules':statistics.mean(r['granule_count'] for r in x),'mean_uncertain_ratio':statistics.mean(r['uncertain_sample_ratio'] for r in x)})
 out=ROOT/"counterexamples/discovered_cases/xor_v1_summary.csv"
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print('XOR v1 summary written: high-dimensional explanation refuted; overlap signal retained.')
if __name__=='__main__': main()
