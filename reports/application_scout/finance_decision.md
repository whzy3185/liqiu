# Finance GB Cheap Test

## Scope

Taiwan Default, Australian Credit, and Polish Bankruptcy (5-year horizon) use
five seeded stratified splits. Each cell compares Raw with its stronger of
cross-fitted GB structural features and OOF purity weighting. Thresholds are
selected on validation MCC; PR-AUC remains threshold-free and primary.

OOF audits passed: **True**.

## Best GB variant versus raw

```text
                        delta_pr_auc                 delta_macro_f1                 delta_mcc                
                                mean  median     std           mean  median     std      mean  median     std
dataset                                                                                                      
australian_credit            -0.0051 -0.0016  0.0115         0.0040  0.0070  0.0186    0.0025  0.0065  0.0390
polish_bankruptcy_5year       0.0025  0.0018  0.0092         0.0012  0.0056  0.0143    0.0043  0.0078  0.0261
taiwan_default               -0.0002  0.0005  0.0026         0.0013  0.0002  0.0057    0.0023  0.0012  0.0065
```

Mean PR-AUC delta: -0.0009; median: 0.0001;
win/tie/loss: 24/0/21.

## Gate

`GO` requires at least three independent financial datasets with mean PR-AUC or
Macro-F1 gain >= +2pp and at least one >= +4pp. This first screen has exactly
three independent tasks, so all three must meet the +2pp condition.

## Decision

**KILL**
