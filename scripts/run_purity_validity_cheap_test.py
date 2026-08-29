"""Run frozen synthetic-oracle adaptive-purity validity test."""
from __future__ import annotations
import argparse
from pathlib import Path
from studies.purity_validity.core import evaluate
def main():
 p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--output',type=Path,default=Path('results/purity_validity_cheap_test.csv'));a=p.parse_args()
 f=evaluate(families=("null_label","smooth_moderate") if a.smoke else ("null_label","smooth_weak","smooth_moderate","piecewise"),sizes=(400,) if a.smoke else (400,1000),seeds=(1,) if a.smoke else (1,7,21,42,2026),oracle_n=10000 if a.smoke else 100000);f.to_csv(a.output,index=False);print({'rows':len(f),'output':str(a.output)})
if __name__=='__main__':main()
