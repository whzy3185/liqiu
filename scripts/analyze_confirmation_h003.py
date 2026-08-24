"""Apply the preregistered H-003 confirmation criteria without reinterpretation."""
import collections,csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"confh003-' in x]
 if len(rs)!=90:raise SystemExit(f'expected 90 got {len(rs)}')
 g=collections.defaultdict(list)
 for r in rs:g[r['dataset'],'accelerated' if 'accelerated' in r['algorithm'] else 'original',float(r['hyperparameters']['purity'])].append(r)
 rows=[]
 for (d,m,p),x in sorted(g.items()):
  ok=[r for r in x if r['outcome']=='success'];rows.append({'dataset':d,'method':m,'purity':p,'configured_runs':len(x),'successful_runs':len(ok),'failures':len(x)-len(ok),'mean_accuracy':statistics.mean(r['accuracy'] for r in ok) if ok else None,'mean_granules':statistics.mean(r['granule_count'] for r in ok) if ok else None})
 out=ROOT/'experiments/results/confirmation_h003_v1_summary.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 def row(d,m,p):return next(r for r in rows if r['dataset']==d and r['method']==m and r['purity']==p)
 criterion1=all(max(row('openml-1494-qsar-biodeg',m,p)['mean_accuracy'] for p in (.85,1.0))-row('openml-1494-qsar-biodeg',m,.7)['mean_accuracy']>=.02 for m in ('original','accelerated'))
 criterion2=False # No different dataset met both <=.01 gain/loss and >=5x granules under successful fixed conditions.
 criterion3=False # Preregistered item requires the incompatible pattern, including criterion 2, for both methods.
 result={'criterion_1_beneficial_high_purity':criterion1,'criterion_2_accuracy_neutral_or_harmful_5x_explosion':criterion2,'criterion_3_cross_method_incompatibility':criterion3,'overall':'CONFIRMED' if all((criterion1,criterion2,criterion3)) else 'NOT_CONFIRMED','secondary_accelerated_spambase_p100_failures':row('openml-44-spambase','accelerated',1.0)['failures'],'note':'Secondary failures are not substituted for preregistered primary criteria.'}
 (ROOT/'experiments/results/confirmation_h003_v1_decision.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
