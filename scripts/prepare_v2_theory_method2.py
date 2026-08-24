"""Clone frozen theory settings for the independent class-mean splitter."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'experiments/configs/v2/theory';target=ROOT/'experiments/configs/v2/theory_method2'
def main():
 target.mkdir(parents=True,exist_ok=True);count=0
 for path in sorted(source.glob('*.json')):
  c=json.loads(path.read_text());c['experiment_id']=c['experiment_id'].replace('v2thy-','v2thym2-',1);c['algorithm']='v2-class-mean-risk-budget-tree-cut';c['dataset_generation_parameters']['generation_method']='class_means';c['search']['campaign']='v2_theory_frontier_method2';(target/f"{c['experiment_id']}.json").write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');count+=1
 print('generated',count,'method2 configs')
if __name__=='__main__':main()
