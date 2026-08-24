"""Aggregate accuracy/structure phase changes across global purity thresholds."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"purv1-' in x]
 if len(rs)!=105: raise SystemExit(f'expected 105, got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs: g[r['dataset'],float(r['hyperparameters']['purity'])].append(r)
 rows=[]
 for (dataset,purity),x in sorted(g.items()):
  rows.append({'dataset':dataset,'purity':purity,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),
   'std_accuracy':statistics.pstdev(r['accuracy'] for r in x),'mean_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),
   'mean_ece':statistics.mean(r['calibration_error'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x),
   'mean_size':statistics.mean(r['average_granule_size'] for r in x),'mean_runtime':statistics.mean(r['runtime_seconds'] for r in x)})
 best={}
 for dataset in sorted({r['dataset'] for r in rows}):
  candidates=[r for r in rows if r['dataset']==dataset]; best[dataset]=max(candidates,key=lambda r:(r['mean_accuracy'],-r['mean_granules']))
 for r in rows: r['accuracy_regret']=best[r['dataset']]['mean_accuracy']-r['mean_accuracy']
 out=ROOT/'counterexamples/discovered_cases/real_purity_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print('Best mean-accuracy purity by dataset:')
 for d,r in best.items(): print(d,r['purity'],round(r['mean_accuracy'],4),round(r['mean_granules'],1))
if __name__=='__main__': main()
