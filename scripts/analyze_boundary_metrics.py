"""Cross-generator predictive audit for Candidate 3 mechanism metrics."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,r2_score
from sklearn.model_selection import GroupKFold,cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
ROOT=Path(__file__).resolve().parents[1];NAMES=('global_knn_mixing','within_ball_knn_mixing','mixed_ball_ratio','weighted_impurity','fragmentation_ratio')
def main():
 rs=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if '"bmv1-' in x]
 if len(rs)!=90:raise SystemExit(f'expected 90 got {len(rs)}')
 rows=[]
 for r in rs:
  p=r['experiment_id'].split('-');rows.append({'experiment_id':r['experiment_id'],'case':p[1],'method':p[2],'accuracy_gap':r['additional_metrics']['accuracy_gap'],'global_knn_mixing':r['additional_metrics']['global_knn_label_mixing'],'within_ball_knn_mixing':r['structure']['within_ball_knn_mixing'],'mixed_ball_ratio':r['structure']['mixed_ball_sample_ratio'],'weighted_impurity':r['structure']['weighted_impurity'],'fragmentation_ratio':r['structure']['fragmentation_ratio']})
 with (ROOT/'experiments/results/boundary_metric_v1_rows.csv').open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 X=np.array([[r[n] for n in NAMES] for r in rows]);y=np.array([r['accuracy_gap'] for r in rows]);groups=np.array([r['case'] for r in rows]);pred=cross_val_predict(make_pipeline(StandardScaler(),Ridge(alpha=1)),X,y,groups=groups,cv=GroupKFold(9));result={'runs':90,'spearman':{n:float(spearmanr(X[:,i],y).statistic) for i,n in enumerate(NAMES)},'leave_case_out_r2':float(r2_score(y,pred)),'leave_case_out_mae':float(mean_absolute_error(y,pred)),'constant_baseline_mae':float(mean_absolute_error(y,np.full(len(y),y.mean())))}
 (ROOT/'experiments/results/boundary_metric_v1_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
