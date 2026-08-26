"""Apply the preregistered raw and KMeans comparison gate."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/application_scout/unsupervised_local_structure.csv'
AUDIT=ROOT/'results/application_scout/unsupervised_local_structure_audit.json'
REPORT=ROOT/'reports/application_scout/unsupervised_local_structure_decision.md'


def main() -> int:
    f=pd.read_csv(SOURCE); keys=['dataset','seed','model']
    raw=f[f.variant=='raw'].set_index(keys); ball=f[f.variant=='ugbfeat'].set_index(keys); km=f[f.variant=='kmeansfeat'].set_index(keys)
    p=ball.join(raw,lsuffix='_ball',rsuffix='_raw').join(km[['macro_f1']],rsuffix='_km')
    p['ball_minus_raw']=p.macro_f1_ball-p.macro_f1_raw; p['ball_minus_kmeans']=p.macro_f1_ball-p.macro_f1
    summary=p.groupby(level='dataset')[['ball_minus_raw','ball_minus_kmeans']].agg(['mean','median','std']).round(4)
    raw_means=p.groupby(level='dataset').ball_minus_raw.mean(); km_means=p.groupby(level='dataset').ball_minus_kmeans.mean()
    decision='GO' if (raw_means>=.01).sum()>=2 and raw_means.max()>=.02 and (km_means>0).sum()>=2 else 'KILL'
    audit=json.loads(AUDIT.read_text())
    REPORT.write_text(f"""# Unsupervised Local-Structure Reopen Test

## Protocol

No label, purity, entropy, class count, or reliability score enters the recursive
ball cover. APS uses a label-free uniform 12,000-row representation subset. A
KMeans cover with the exact same region count receives the same feature schema
and downstream model budget.

Region-count match: **{all(v['n_regions']==v['kmeans_regions'] for v in audit.values())}**.

## Matched Macro-F1 deltas

```text
{summary.to_string()}
```

Mean ball-minus-raw: {p.ball_minus_raw.mean():.4f}; mean ball-minus-KMeans:
{p.ball_minus_kmeans.mean():.4f}. Raw win/tie/loss: {(p.ball_minus_raw>0).sum()}/{(p.ball_minus_raw==0).sum()}/{(p.ball_minus_raw<0).sum()}.

## Decision

**{decision}**

The gate requires two datasets at least +1pp over Raw, one at least +2pp, and
positive ball-minus-KMeans means on two datasets. Failure closes all local
structure feature variants on this application branch.
""",encoding='utf-8')
    print(json.dumps({'decision':decision,'raw_means':raw_means.to_dict(),'kmeans_means':km_means.to_dict()},indent=2));return 0


if __name__=='__main__':raise SystemExit(main())

