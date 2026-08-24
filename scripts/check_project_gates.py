"""Machine-check the explicit ranking/survivor gates, not full TASK 0–25 completion."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from counterexamples.generators import FAMILIES,STREAM_KINDS
def main():
 papers=list(csv.DictReader((ROOT/'literature/papers.csv').open(encoding='utf-8')));matrix=list(csv.DictReader((ROOT/'taxonomy/component_matrix.csv').open(encoding='utf-8')));records=[json.loads(x) for x in (ROOT/'experiments/results/experiments.jsonl').read_text().splitlines() if x];report=(ROOT/'reports/final_research_report.md').read_text();survivors=(ROOT/'candidates/survivors.md').read_text();confirmation=json.loads((ROOT/'experiments/results/confirmation_h003_v1_decision.json').read_text())
 gates={'papers_at_least_100':len(papers)>=100,'matrix_aligned':len(matrix)==len(papers),'five_core_paths':(ROOT/'scripts/check_baselines.py').exists(),'synthetic_families_at_least_10':len(FAMILIES)>=10,'stream_kinds':len(STREAM_KINDS),'experiment_records':len(records),'top10_templates':all(f'\n# Candidate {i}\n' in report for i in range(1,11)),'survivor_count':survivors.count('## P1 —')+survivors.count('## P0 —')+survivors.count('## P2 —'),'confirmation_decision':confirmation['overall'],'pending_configs':__import__('scripts.research_cycle',fromlist=['pending_configs']).pending_configs().__len__()}
 assert gates['papers_at_least_100'] and gates['matrix_aligned'] and gates['five_core_paths'] and gates['synthetic_families_at_least_10'] and gates['top10_templates'] and 2<=gates['survivor_count']<=5 and gates['pending_configs']==0
 print(json.dumps(gates,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
