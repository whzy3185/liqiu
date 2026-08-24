"""Aggregate accelerated method and compare global-purity regimes."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def aggregate(prefix):
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if f'"{prefix}-' in x]; g=collections.defaultdict(list)
 for r in rs: g[r['dataset'],float(r['hyperparameters']['purity'])].append(r)
 rows=[]
 for (d,p),x in sorted(g.items()): rows.append({'dataset':d,'purity':p,'runs':len(x),'mean_accuracy':statistics.mean(r['accuracy'] for r in x),'std_accuracy':statistics.pstdev(r['accuracy'] for r in x),'mean_gap':statistics.mean(r['additional_metrics']['accuracy_gap'] for r in x),'mean_granules':statistics.mean(r['granule_count'] for r in x),'mean_runtime':statistics.mean(r['runtime_seconds'] for r in x)})
 return rows
def main():
 accelerated=aggregate('purav1');
 if sum(r['runs'] for r in accelerated)!=105: raise SystemExit('accelerated scan incomplete')
 out=ROOT/'counterexamples/discovered_cases/accelerate_purity_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(accelerated[0])); w.writeheader(); w.writerows(accelerated)
 print('Accelerated best purity by dataset:')
 for d in sorted({r['dataset'] for r in accelerated}):
  r=max((x for x in accelerated if x['dataset']==d),key=lambda x:(x['mean_accuracy'],-x['mean_granules'])); print(d,r['purity'],round(r['mean_accuracy'],4),round(r['mean_granules'],1))
if __name__=='__main__': main()
