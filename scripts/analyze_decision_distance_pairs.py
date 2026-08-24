"""Pair nearest-center v1 and author boundary-distance v2 runs."""
import csv,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 records={r['experiment_id']:r for r in map(json.loads,(ROOT/'experiments/results/experiments.jsonl').open())};rows=[]
 for p1,p2 in (('xorv1','xorv2'),('altv1','altv2')):
  for k,r in records.items():
   if k.startswith(p1):
    r2=records[k.replace(p1,p2,1)];a=r['additional_metrics']['accuracy_gap'];b=r2['additional_metrics']['accuracy_gap'];rows.append({'v1_id':k,'v2_id':r2['experiment_id'],'nearest_center_gap':a,'center_minus_radius_gap':b,'gap_shift':b-a,'sign_flip':int(np.sign(a)!=np.sign(b)),'failure_threshold_flip':int((a<-.05)!=(b<-.05))})
 out=ROOT/'experiments/results/decision_distance_paired_v1_v2.csv'
 with out.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 a=np.array([r['nearest_center_gap'] for r in rows]);b=np.array([r['center_minus_radius_gap'] for r in rows]);summary={'pairs':len(rows),'nearest_center_mean_gap':float(a.mean()),'center_minus_radius_mean_gap':float(b.mean()),'mean_absolute_gap_shift':float(np.mean(abs(b-a))),'gap_correlation':float(np.corrcoef(a,b)[0,1]),'sign_flips':sum(r['sign_flip'] for r in rows),'failure_threshold_flips':sum(r['failure_threshold_flip'] for r in rows)}
 (ROOT/'experiments/results/decision_distance_paired_v1_v2.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
