"""Aggregate Candidate 4 GBC-vs-RF conformal utility audit."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"c4cv1-' in x]
 if len(rs)!=30:raise SystemExit(f'expected 30 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:g[r['dataset'],float(r['hyperparameters']['alpha'])].append(r)
 rows=[]
 for (d,a),x in sorted(g.items()):
  rows.append({'dataset':d,'alpha':a,'runs':len(x),'gbc_coverage':statistics.mean(r['additional_metrics']['gbc_conformal']['coverage'] for r in x),'gbc_set_size':statistics.mean(r['additional_metrics']['gbc_conformal']['average_set_size'] for r in x),'gbc_singleton_ratio':statistics.mean(r['additional_metrics']['gbc_conformal']['singleton_ratio'] for r in x),'rf_coverage':statistics.mean(r['additional_metrics']['rf_conformal']['coverage'] for r in x),'rf_set_size':statistics.mean(r['additional_metrics']['rf_conformal']['average_set_size'] for r in x),'rf_singleton_ratio':statistics.mean(r['additional_metrics']['rf_conformal']['singleton_ratio'] for r in x)})
 out=ROOT/'experiments/results/c4_conformal_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
