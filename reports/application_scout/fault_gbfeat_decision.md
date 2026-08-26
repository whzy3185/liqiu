# Industrial GB Structural-Feature Cheap Test

## Scope

Three independent real industrial tabular sources, five seeds, and five strong
tree/boosting models are compared in matched cells. Training GB features are
5-fold out of fold; validation/test features use a generator fitted only on
training data. OOF audit passed: **True**.

APS generator fitting is capped at a stratified 12,000 training rows per fold
for CPU cost; downstream raw and GBFeat models both use all 48,000 training rows.

## Dataset-level deltas

```text
             delta_macro_f1                 delta_balanced_accuracy                 delta_mcc                
                       mean  median     std                    mean  median     std      mean  median     std
dataset                                                                                                      
aps_failure         -0.0004  0.0000  0.0053                  0.0003 -0.0002  0.0059   -0.0007  0.0000  0.0099
secom                0.0000  0.0000  0.0005                  0.0001  0.0000  0.0009    0.0002  0.0000  0.0062
steel_plates        -0.0190 -0.0159  0.0238                 -0.0291 -0.0307  0.0267   -0.0161 -0.0167  0.0185
```

## Macro-F1 gain counts

```text
{
  ">0": 19,
  ">=1pp": 3,
  ">=2pp": 1,
  ">=3pp": 0,
  ">=5pp": 0,
  "total": 75
}
```

Overall mean delta: -0.0065; median: 0.0000;
win/tie/loss: 19/22/34.

## Resource structure

Mean full generator ball count: 86.0; mean compression ratio:
0.0737; mean GB feature time per dataset/seed:
0.51 seconds.

## Gate

`GO` requires all three independent sources to average at least +2pp Macro-F1
and one source to average at least +4pp. A majority of matched declines kills
this feature mechanism.

## Decision

**KILL**
