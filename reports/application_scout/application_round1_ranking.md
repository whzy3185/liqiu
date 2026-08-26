# Application Round-1 Ranking

## Result

No application satisfies the minimum retention standard. Therefore:

| Slot | Decision |
|---|---|
| KEEP 1 | **None** |
| BACKUP 1 | **None** |
| Industrial fault | KILL |
| Financial risk / fraud | KILL |
| IIoT intrusion | KILL |
| Medical | Not run; backup only and no surviving mechanism to justify expansion |

The instruction to select one KEEP and one BACKUP conflicts with the frozen
performance gates. This report follows the higher-priority experimental rule:
do not retain a direction without a stable material gain.

## Evidence table

| Domain | Independent tasks screened | Primary metric | Mean GB delta | Median GB delta | Win/tie/loss | >=1pp | >=2pp | >=3pp | Decision |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| Industrial tabular | 3 | Macro-F1 | -0.65pp | 0.00pp | 19/22/34 | 3 | 1 | 0 | KILL |
| Finance | 3 | PR-AUC | -0.09pp | +0.01pp | 24/0/21 | 0 | 0 | 0 | KILL |
| IIoT diagnostic | 1 | PR-AUC | -0.0002pp | +0.001pp | 9/0/6 | 0 | 0 | 0 | KILL |

`>=1pp` and larger counts are paired method/seed cells. For IIoT the raw PR-AUC
was already 0.995--0.997 in a transformed random-split export, so decimal-scale
fluctuation is not evidence of a useful gain.

## Industrial fault diagnosis

The initial application screen used Steel Plates Faults, SECOM semiconductor
yield, and Scania APS failure because official mechanical-vibration downloads
from CWRU/HUST/UConn/SEU were unavailable or severely throttled in this runtime.
This is an honest *industrial tabular mechanism screen*, not a substitute for
the planned vibration-signal paper pool.

Raw models were strong where the task was learnable: APS LightGBM Macro-F1
0.9095 and Steel XGBoost 0.7898. Cross-fitted structural features had mean
Macro-F1 deltas of -0.04pp (APS), +0.00pp (SECOM), and -1.90pp (Steel). SECOM's
chronological future block caused every model to predict the majority class;
GB features did not repair that hard temporal shift.

The structural-feature mechanism is therefore `KILL`. The prerequisite for GB
sample weighting, few-shot, imbalance, label-noise, signal-noise, and
cross-condition expansion is closed. This branch does not interpret the lack of
downloadable vibration data as evidence that GB works there.

## Financial risk / fraud

Taiwan Default, Australian Credit, and Polish Bankruptcy (5-year horizon) had
the best literature-space/data-quality combination. Each seed selected GBFeat or
OOF purity weighting by **validation** PR-AUC, then evaluated that frozen choice
once on test data. OOF audits passed for all 15 dataset/seed cells.

The best selected GB variant averaged -0.51pp PR-AUC on Australian Credit,
+0.25pp on Polish Bankruptcy, and -0.02pp on Taiwan Default. The overall mean
was -0.09pp. Even the only positive task was an order of magnitude below the
predeclared +2pp retention threshold. Finance is `KILL` for this mechanism
family.

## IIoT intrusion

The direct 2026 GBIFS collision establishes a high novelty/performance bar.
Only the transformed OpenML UNSW-NB15 export was available during the execution
window. It was stripped of `id`, export row index, and `attack_cat`, but it lacks
the raw campaign, time, device, IP and port metadata required for a primary
leakage-safe protocol. X-IIoTID and WUSTL-IIOT official sources were not
downloaded due to host availability/throughput.

The diagnostic result is null: mean PR-AUC delta -0.000002 and mean positive
recall delta -0.00008. This is `KILL`, both because no material effect appeared
and because one transformed random-split source cannot satisfy the IIoT gate.

## Scoring against the Prompt-17 criteria

| Criterion | Industrial | Finance | IIoT |
|---|---|---|---|
| Performance improvement, 35% | 1/5 | 1/5 | 1/5 |
| Multi-source consistency, 15% | 1/5 | 1/5 | 1/5 |
| Recent literature space, 15% | 2/5 | 4/5 | 2/5 |
| Application value, 10% | 5/5 | 5/5 | 5/5 |
| Data quality, 10% | 3/5 | 4/5 | 1/5 |
| Reproducibility, 10% | 3/5 | 5/5 | 2/5 |
| Compute cost, 5% | 4/5 | 4/5 | 3/5 |
| Weighted score | 2.10/5 | 2.55/5 | 1.80/5 |

Finance has the best opportunity score but fails the only criterion that can
justify an application paper: stable performance improvement. It is ranked first
only as the least-negative evidence line, not as a retained research direction.

## Frozen stop point

Prompt 17 is complete. Prompts 18--29 are not authorized because there is no
KEEP application and no GB module to shrink, tune, ablate, or compare to SOTA.

To reopen this project, first obtain at least three official mechanical-vibration
sources under recording/unit/condition splits and run a **new, preregistered
mechanism** (not a parameter search over the killed structural features/purity
weights). The hypothesis must explain why it is expected to address a failure
mode that this screen did not.

## Decision

**KILL**

