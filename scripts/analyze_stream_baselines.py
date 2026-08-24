"""Aggregate prequential streaming controls."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"strv1-' in x]
 if len(rs)!=72:raise SystemExit(f'expected 72 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:g[r['dataset'].replace('synthetic-stream-','').replace('-v1',''),r['hyperparameters']['strategy']].append(r)
 rows=[]
 for (kind,strategy),x in sorted(g.items()):rows.append({'kind':kind,'strategy':strategy,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),'mean_macro_f1':statistics.mean(r['macro_f1'] for r in x),'mean_update_seconds':statistics.mean(r['additional_metrics']['mean_update_seconds'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x if r['granule_count'] is not None) if any(r['granule_count'] is not None for r in x) else None,'emerging_recall':statistics.mean(r['additional_metrics']['emerging_class_recall'] for r in x if r['additional_metrics']['emerging_class_recall'] is not None) if any(r['additional_metrics']['emerging_class_recall'] is not None for r in x) else None})
 out=ROOT/'experiments/results/stream_baseline_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
