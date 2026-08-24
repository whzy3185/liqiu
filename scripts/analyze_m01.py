"""Compare M01 Wilson lower-bound stop with observed-purity p=.85 baseline."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 lines=(ROOT/'experiments/results/experiments.jsonl').read_text().splitlines(); m=[json.loads(x) for x in lines if '"m01v1-' in x]; b=[json.loads(x) for x in lines if '"purv1-' in x and '"purity": 0.85' in x]
 if len(m)!=15 or len(b)!=15: raise SystemExit(f'incomplete {len(m)} {len(b)}')
 gm=collections.defaultdict(list); gb=collections.defaultdict(list)
 for r in m: gm[r['dataset']].append(r)
 for r in b: gb[r['dataset']].append(r)
 rows=[]
 for d in sorted(gm):
  mr,br=gm[d],gb[d]; rows.append({'dataset':d,'m01_accuracy':statistics.mean(r['accuracy'] for r in mr),'baseline_accuracy':statistics.mean(r['accuracy'] for r in br),
   'accuracy_delta':statistics.mean(r['accuracy'] for r in mr)-statistics.mean(r['accuracy'] for r in br),'m01_granules':statistics.mean(r['granule_count'] for r in mr),
   'baseline_granules':statistics.mean(r['granule_count'] for r in br),'granule_delta':statistics.mean(r['granule_count'] for r in mr)-statistics.mean(r['granule_count'] for r in br)})
 out=ROOT/'experiments/results/m01_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
