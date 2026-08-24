"""Aggregate corrected boundary-distance v2 replications."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def write(records,kind,out):
 g=collections.defaultdict(list)
 for r in records:
  p=r['experiment_id'].split('-'); key=(p[1],p[2],p[3]) if kind=='xor' else (p[1],p[2])
  g[key].append(r)
 rows=[]
 for key,x in sorted(g.items()):
  base={'key':'/'.join(key),'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),
        'mean_reference_accuracy':statistics.mean(r['additional_metrics']['reference_accuracy'] for r in x),
        'mean_accuracy_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),
        'negative_gap_runs':sum(r['additional_metrics']['accuracy_gap']<0 for r in x),
        'mean_granules':statistics.mean(r['granule_count'] for r in x)}; rows.append(base)
 with (ROOT/out).open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def main():
 lines=(ROOT/'experiments/results/experiments.jsonl').read_text().splitlines(); xor=[json.loads(x) for x in lines if '"xorv2-' in x]; alt=[json.loads(x) for x in lines if '"altv2-' in x]
 if len(xor)!=140 or len(alt)!=90: raise SystemExit(f'incomplete v2: {len(xor)}, {len(alt)}')
 write(xor,'xor','counterexamples/discovered_cases/xor_v2_summary.csv'); write(alt,'alt','counterexamples/discovered_cases/alternating_v2_summary.csv')
 print('Corrected v2 summaries written: 230/230 records.')
if __name__=='__main__': main()
