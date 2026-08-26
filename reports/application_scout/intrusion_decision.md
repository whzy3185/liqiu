# IIoT / Intrusion GB Quick Screen

## Data limitation

Only the transformed OpenML UNSW-NB15 export was obtainable within the execution
window. It removes `id` and `attack_cat`, but it lacks original campaign, IP,
port and timestamp metadata needed for a primary leakage-safe result. X-IIoTID
and WUSTL-IIOT official downloads were not completed because their source hosts
were unavailable or severely rate-limited. This screen is diagnostic only.

## Matched deltas after validation-only variant selection

```text
            seed  delta_pr_auc  delta_macro_f1  delta_mcc  delta_recall_positive
count    15.0000       15.0000         15.0000    15.0000                15.0000
mean    419.4000       -0.0000         -0.0003    -0.0006                -0.0001
std     831.6227        0.0001          0.0004     0.0009                 0.0032
min       1.0000       -0.0001         -0.0011    -0.0024                -0.0046
25%       7.0000       -0.0000         -0.0006    -0.0014                -0.0024
50%      21.0000        0.0000         -0.0003    -0.0006                -0.0006
75%      42.0000        0.0001          0.0000     0.0002                 0.0025
max    2026.0000        0.0001          0.0002     0.0005                 0.0061
```

OOF audit passed: **True**.
Mean PR-AUC delta: -0.0000; mean rare/positive recall
delta: -0.0001.

## Decision

**KILL**

The preregistered IIoT gate requires multiple leakage-safe scenario/device/time
datasets plus either +3pp mean primary-metric gain or +5pp minority recall. One
transformed random-split diagnostic export cannot satisfy it, regardless of its
score. No further IIoT GB tuning is authorized.
