"""Finite-budget automated research cycle over configuration-recorded experiments."""
import argparse,datetime as dt,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_core import run_from_config
RESULTS=ROOT/'experiments/results/experiments.jsonl'
def records():return [json.loads(x) for x in RESULTS.read_text(encoding='utf-8').splitlines() if x]
def pending_configs():
 done={r['experiment_id'] for r in records()};pending=[]
 for path in sorted((ROOT/'experiments/configs').rglob('*.json')):
  try:c=json.loads(path.read_text(encoding='utf-8'))
  except json.JSONDecodeError:continue
  if not {'experiment_id','runner','algorithm','dataset','pool','seed'}<=set(c):continue
  if c['experiment_id'] not in done:pending.append(path)
 return pending
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'experiments/configs/research_cycle.json');p.add_argument('--dry-run',action='store_true');p.add_argument('--max-experiments',type=int);a=p.parse_args();cfg=json.loads(a.config.read_text());pending=pending_configs();limit=a.max_experiments if a.max_experiments is not None else int(cfg['max_new_experiments_per_cycle']);before=len(records());summary={'date_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'records_before':before,'pending_before':len(pending),'budget':limit,'executed':[],'post_commands':[]}
 print(json.dumps({'records':before,'pending':len(pending),'budget':limit,'next':[str(x.relative_to(ROOT)) for x in pending[:limit]]},indent=2))
 if a.dry_run:return 0
 for path in pending[:limit]:
  r=run_from_config(path,RESULTS);summary['executed'].append({'experiment_id':r['experiment_id'],'outcome':r['outcome'],'config':str(path.relative_to(ROOT))})
 for command in cfg.get('post_commands',[]):
  command=[sys.executable if x=='python' else x for x in command];proc=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);summary['post_commands'].append({'command':command,'returncode':proc.returncode,'output_tail':proc.stdout[-4000:]});
  if proc.returncode:summary['status']='post-check-failure';break
 else:summary['status']='ok'
 summary['records_after']=len(records());summary['pending_after']=len(pending_configs());(ROOT/'reports/daily/cycle_latest.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,ensure_ascii=False));return 0 if summary['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
