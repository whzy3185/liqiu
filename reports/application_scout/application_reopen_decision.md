# Application Scout Reopen Decision

## Reopened mechanism

After the first round killed supervised GB structural features and OOF purity
weights, one distinct label-free mechanism was preregistered: recursive
geometric ball-cover features. It was tested against both Raw and a KMeans cover
with the exact same number of regions.

## Result

| Comparison | APS | SECOM | Steel | Overall |
|---|---:|---:|---:|---:|
| UGBFeat - Raw Macro-F1 | -0.13pp | -0.01pp | -0.07pp | -0.07pp |
| UGBFeat - matched KMeans Macro-F1 | -0.05pp | 0.00pp | +0.65pp | +0.20pp |

No dataset reached the preregistered +1pp Raw gain and none reached +2pp. The
test therefore fails both the absolute-performance and GB-specificity gates.

## Mechanism ledger

| Mechanism | Label use during construction | Strong control | Outcome |
|---|---|---|---|
| Supervised GB structural features | purity/label statistics, OOF for train | Raw only in first screen | KILL |
| OOF purity reliability weighting | training labels only | Raw | KILL in finance; industrial gate closed |
| Unsupervised recursive ball features | none | matched-count KMeans | KILL |

## Final application-scout state

**KILL**

No further variant of local granular-ball structure features, purity weighting,
or geometric ball coverage is authorized on this branch. A future restart needs
a new hypothesis tied to a distinct observable mechanism, fresh preregistration,
and real sensor data available under recording/unit/condition splits.

