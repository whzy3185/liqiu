"""Aggregate Candidate 2 sequential evidence control."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"c2sv1-' in x]
 if len(rs)!=30:raise SystemExit(f'expected 30 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:g[r['dataset'],float(r['hyperparameters']['delta'])].append(r)
 rows=[]
 for (d,delta),x in sorted(g.items()):rows.append({'dataset':d,'delta':delta,'runs':len(x),'fallback_runs':sum(r['additional_metrics']['selected_purity']==.85 for r in x),'mean_observation_fraction':statistics.mean(r['additional_metrics']['observation_fraction'] for r in x),'mean_accuracy_delta':statistics.mean(r['additional_metrics']['accuracy_delta'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x)})
 out=ROOT/'experiments/results/c2_sequential_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
