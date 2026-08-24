import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CLIENTS=(5,10,20);ALPHAS=(.05,.1,.3,1.0);SEEDS=(1,7,21,42,2026)
def main():
 out=ROOT/'experiments/configs/v2/federated';out.mkdir(parents=True,exist_ok=True);count=0
 for clients in CLIENTS:
  for alpha in ALPHAS:
   for seed in SEEDS:
    eid=f'v2fed-digits-c{clients}-a{int(alpha*100):03d}-s{seed}';cfg={'experiment_id':eid,'study':'federated-risk-granularity-v2','algorithm':'federated-prototype-budget-frontier','dataset':'sklearn-digits','dataset_generation_parameters':{'clients':clients,'alpha':alpha,'quantity_ratio_target':5},'pool':'exploration','seed':seed,'runner':'experiments.runners.v2_federated_digits:run','hyperparameters':{'thresholds':[.55,.60,.65,.70,.75,.80,.85,.90,.95,1.0],'budget_fractions':[0,.25,.5,.75,1.0],'server_models':['nearest','logistic','mlp']},'search':{'enabled':False,'campaign':'v2_federated_digits_v1'}};(out/f'{eid}.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n');count+=1
 print('generated',count,'federated configs')
if __name__=='__main__':main()
