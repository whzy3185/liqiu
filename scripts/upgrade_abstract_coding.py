"""Upgrade metadata-only rows via OpenAlex abstracts without redistributing text."""
import csv,json,subprocess,sys,time,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.fetch_literature import COMPONENT_FIELDS,PAPER_FIELDS,_component_row,_clean_text
def abstract(index):
 if not index:return ''
 size=max(p for positions in index.values() for p in positions)+1;words=['']*size
 for word,positions in index.items():
  for p in positions:words[p]=word
 return _clean_text(' '.join(words))
def fetch(doi,cache):
 if doi in cache:return cache[doi]
 url='https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe='/.:-_()');p=subprocess.run(['curl','-sS','-L','--max-time','25','-A','granular-research-lab/0.1',url],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:data=json.loads(p.stdout) if p.returncode==0 else {}
 except json.JSONDecodeError:data={}
 cache[doi]=data;return data
def main():
 paper_path=ROOT/'literature/papers.csv';component_path=ROOT/'taxonomy/component_matrix.csv';json_path=ROOT/'literature/papers.jsonl';papers=list(csv.DictReader(paper_path.open(encoding='utf-8')));components=list(csv.DictReader(component_path.open(encoding='utf-8')));by_component={r['paper_id']:r for r in components};cache_path=ROOT/'work/openalex_abstracts.json';cache=json.loads(cache_path.read_text()) if cache_path.exists() else {};upgraded=[]
 for row in papers:
  if row['abstract_status']!='not-available-from-enrichment' or not row['doi']:continue
  data=fetch(row['doi'],cache);text=abstract(data.get('abstract_inverted_index'))
  cache_path.parent.mkdir(parents=True,exist_ok=True);cache_path.write_text(json.dumps(cache,ensure_ascii=False),encoding='utf-8')
  if not text:continue
  item={'_title':row['title'],'_year':int(row['year']),'_abstract':text,'container-title':[row['venue']]};coded=_component_row(item,row['paper_id'],row['primary_source_url']);by_component[row['paper_id']].update(coded);row['abstract_status']='available-and-coded-not-redistributed';row['verification_status']='publisher-metadata+openalex-abstract-coded';row['openalex_id']=data.get('id','');upgraded.append(row['paper_id']);print('upgraded',row['paper_id'],row['title'],flush=True)
  if sum(r['abstract_status']=='available-and-coded-not-redistributed' for r in papers)>=100:break
  time.sleep(.1)
 with paper_path.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=PAPER_FIELDS,lineterminator='\n');w.writeheader();w.writerows(papers)
 with component_path.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=COMPONENT_FIELDS,lineterminator='\n');w.writeheader();w.writerows([by_component[r['paper_id']] for r in components])
 json_rows=[json.loads(x) for x in json_path.read_text(encoding='utf-8').splitlines() if x]
 paper_by={r['paper_id']:r for r in papers}
 for r in json_rows:
  p=paper_by[r['paper_id']];r['abstract_status']=p['abstract_status'];r['verification_status']=p['verification_status'];r['openalex_id']=p['openalex_id']
 with json_path.open('w',encoding='utf-8') as h:
  for r in json_rows:h.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
 print(json.dumps({'upgraded':len(upgraded),'ids':upgraded,'abstract_coded_total':sum(r['abstract_status']=='available-and-coded-not-redistributed' for r in papers)},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
