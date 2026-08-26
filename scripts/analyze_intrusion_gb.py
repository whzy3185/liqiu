"""Report diagnostic IIoT screen without overstating leakage-safe evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/application_scout/intrusion_gb.csv'
AUDIT=ROOT/'results/application_scout/intrusion_gb_audit.json'
REPORT=ROOT/'reports/application_scout/intrusion_decision.md'


def main() -> int:
    frame=pd.read_csv(SOURCE)
    raw=frame[frame.variant=='raw'].set_index(['seed','model'])
    alternatives=frame[frame.variant!='raw']
    chosen=[]
    for key,group in alternatives.groupby(['seed','model']):
        best=group.sort_values('validation_pr_auc',ascending=False).iloc[0]
        base=raw.loc[key]
        chosen.append({'seed':key[0],'model':key[1],'variant':best.variant,'delta_pr_auc':best.pr_auc-base.pr_auc,'delta_macro_f1':best.macro_f1-base.macro_f1,'delta_mcc':best.mcc-base.mcc,'delta_recall_positive':best.recall_positive-base.recall_positive})
    paired=pd.DataFrame(chosen)
    audit=json.loads(AUDIT.read_text())
    REPORT.write_text(f"""# IIoT / Intrusion GB Quick Screen

## Data limitation

Only the transformed OpenML UNSW-NB15 export was obtainable within the execution
window. It removes `id` and `attack_cat`, but it lacks original campaign, IP,
port and timestamp metadata needed for a primary leakage-safe result. X-IIoTID
and WUSTL-IIOT official downloads were not completed because their source hosts
were unavailable or severely rate-limited. This screen is diagnostic only.

## Matched deltas after validation-only variant selection

```text
{paired.describe().round(4).to_string()}
```

OOF audit passed: **{all(v['oof_disjoint'] for v in audit.values())}**.
Mean PR-AUC delta: {paired.delta_pr_auc.mean():.4f}; mean rare/positive recall
delta: {paired.delta_recall_positive.mean():.4f}.

## Decision

**KILL**

The preregistered IIoT gate requires multiple leakage-safe scenario/device/time
datasets plus either +3pp mean primary-metric gain or +5pp minority recall. One
transformed random-split diagnostic export cannot satisfy it, regardless of its
score. No further IIoT GB tuning is authorized.
""",encoding='utf-8')
    print(json.dumps({'mean_pr_auc_delta':float(paired.delta_pr_auc.mean()),'mean_recall_delta':float(paired.delta_recall_positive.mean()),'decision':'KILL'},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())

