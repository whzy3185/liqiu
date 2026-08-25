# Multi-Auditor Cheap Test D

## Scope

Auditor populations of 20, 50, and 100 are tested under noisy, lazy,
malicious, colluding, adaptive, and drifting behavior. Every method receives the
same history and current response matrix.

## Mean results

```text
           method  final_audit_accuracy  malicious_auroc  false_trust_rate  additional_audit_cost  decision_delay
  beta_reputation                0.9216           0.7181            0.4778                  0.000          1.4805
      dawid_skene                0.7691           0.7582            0.2014                  0.000          1.4805
     gb_three_way                0.9373           0.6201            0.7561                  1.425          1.4943
    granular_ball                0.9109           0.6177            0.7561                  0.000          1.4805
     kmeans_trust                0.9109           0.6184            0.7561                  0.000          1.4805
   knn_competence                0.9218           0.7181            0.4778                  0.000          1.4805
    majority_vote                0.8397           0.5000            1.0000                  0.000          1.4805
   tree_partition                0.9118           0.6148            0.7561                  0.000          1.4805
weighted_majority                0.9532           0.7181            0.4778                  0.000          1.5005
```

## GB-specific gate

- Matched conditions: 120
- Mean GB accuracy gain over the strongest non-GB method: -0.0196
- Fraction with at least +0.01 gain: 0.000
- Non-loss fraction: 0.442

The strongest comparator is selected per condition from weighted majority,
Beta reputation, Dawid-Skene, matched KMeans, kNN competence, and matched tree
partitions. Failed configurations: 0.

## Decision

**KILL**
