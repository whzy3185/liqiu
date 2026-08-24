"""Create immutable rerun IDs for the Citeseer loader alias fix."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'experiments/configs/v2/gnn';target=ROOT/'experiments/configs/v2/gnn_citeseer_fix'
def main():
 target.mkdir(parents=True,exist_ok=True);count=0
 for path in sorted(source.glob('v2gnn-citeseer-*.json')):
  c=json.loads(path.read_text());c['experiment_id']=c['experiment_id'].replace('v2gnn-','v2gnnfix-',1);c['search']['campaign']='v2_gnn_frontier_citeseer_loader_fix';c['search']['corrects']='Citeseer extended-matrix in-place reorder alias';(target/f"{c['experiment_id']}.json").write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');count+=1
 print('generated',count,'Citeseer corrected configs')
if __name__=='__main__':main()
