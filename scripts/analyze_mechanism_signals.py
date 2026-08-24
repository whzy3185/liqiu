"""Test whether recorded ball statistics explain targeted failure gaps."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1]
def corr(x,y):
 return {'pearson':float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 else None,
         'spearman':float(spearmanr(x,y).statistic) if np.std(x)>0 else None}
def main():
 records=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"xorv2-' in x or '"altv2-' in x]
 rows=[]
 for r in records:
  sizes=np.asarray(r['structure']['ball_sizes'],float); purity=np.asarray(r['structure']['ball_purities'],float)
  rows.append({'method':'adaptive' if 'adaptive' in r['algorithm'] else 'original','gap':r['additional_metrics']['accuracy_gap'],
               'weighted_impurity':float(np.sum(sizes*(1-purity))/sizes.sum()),'low_purity_coverage':r['uncertain_sample_ratio'],
               'granules':r['granule_count'],'mean_size':r['average_granule_size']})
 result={'runs':len(rows),'all':{},'by_method':{}}
 for name,subset in [('all',rows),('original',[r for r in rows if r['method']=='original']),('adaptive',[r for r in rows if r['method']=='adaptive'])]:
  gaps=np.array([r['gap'] for r in subset]); stats={k:corr(np.array([r[k] for r in subset]),gaps) for k in ('weighted_impurity','low_purity_coverage','granules','mean_size')}
  stats['runs']=len(subset); stats['zero_low_purity_runs']=sum(r['low_purity_coverage']==0 for r in subset)
  if name=='all': result['all']=stats
  else: result['by_method'][name]=stats
 out=ROOT/'counterexamples/discovered_cases/mechanism_signals_v2.json'; out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
