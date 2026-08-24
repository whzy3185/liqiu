"""Compare clean-room GBC to author gb_knn functions on fixed data."""
import importlib.util,sys
from pathlib import Path
import numpy as np
from sklearn.datasets import make_moons
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from baselines.gbc import GranularBallClassifier
def load(path):
 spec=importlib.util.spec_from_file_location('author_gb_knn',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def main():
 X,y=make_moons(n_samples=300,noise=.12,random_state=42); author=load(ROOT/'work/upstreams/syxiaa_GBC/gb_knn.py')
 data=np.column_stack([y,X]); balls=[data]
 while True:
  before=len(balls); balls=author.splits(balls,.85)
  if len(balls)==before: break
 clean=GranularBallClassifier(.85).fit(X,y)
 author_sizes=sorted(len(b) for b in balls); clean_sizes=sorted(len(b.members) for b in clean.balls_)
 assert author_sizes==clean_sizes,(author_sizes,clean_sizes)
 test=X[::7]; author_pred=[]
 for row in test:
  distances=[]
  for b in balls:
   center,radius,_=author.calculate_center_and_radius(b); label,_=author.get_label_and_purity(b); distances.append((np.linalg.norm(row-center)-radius,label))
  author_pred.append(min(distances,key=lambda z:z[0])[1])
 np.testing.assert_array_equal(author_pred,clean.predict(test))
 print(f'Clean-room GBC matches author code: {len(balls)} balls and {len(test)} boundary-distance predictions.')
if __name__=='__main__': main()
