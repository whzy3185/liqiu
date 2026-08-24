"""Aggregate the minimal H-003 incompatibility construction."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"th003v1-' in x]
 if len(rs)!=40:raise SystemExit(f'expected 40 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:g[r['dataset'],float(r['hyperparameters']['purity'])].append(r)
 rows=[]
 for (d,t),x in sorted(g.items()):rows.append({'dataset':d,'purity':t,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),'std_accuracy':statistics.pstdev(r['accuracy'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x),'min_granules':min(r['granule_count'] for r in x),'max_granules':max(r['granule_count'] for r in x)})
 out=ROOT/'experiments/results/theory_h003_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
