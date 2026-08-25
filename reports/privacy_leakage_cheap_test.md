# Privacy Leakage Cheap Test A

## Scope

Five exploration datasets, five frozen seeds, CPU-only execution, and matched
representative counts. Membership results come from a cross-validated attack on
distance and only the statistics actually disclosed by each R0-R8 release.
These are empirical leakage measurements, not formal privacy guarantees.

## Aggregate results

```text
       method                       variant  membership_roc_auc_mean  membership_roc_auc_std  attribute_accuracy_mean  attribute_accuracy_std  reconstruction_mse_mean  reconstruction_mse_std  utility_accuracy_mean  utility_accuracy_std  compression_ratio_mean  compression_ratio_std
granular_ball                     R5_center                   0.7177                  0.1540                   0.8238                  0.1159                   0.1584                  0.2127                 0.7607                0.1210                  0.2773                 0.2005
granular_ball              R6_center_radius                   0.6991                  0.1579                   0.8238                  0.1159                   0.1700                  0.2230                 0.7879                0.1106                  0.2773                 0.2005
granular_ball        R7_center_radius_count                   0.6998                  0.1572                   0.8238                  0.1159                   0.1700                  0.2230                 0.7879                0.1106                  0.2773                 0.2005
granular_ball R8_center_radius_count_purity                   0.6998                  0.1572                   0.8238                  0.1159                   0.1700                  0.2230                 0.7879                0.1106                  0.2773                 0.2005
 hierarchical                  matched_full                   0.7424                  0.1218                   0.9361                  0.0624                   0.1222                  0.2042                 0.7766                0.1137                  0.2773                 0.2005
       kmeans                     R1_center                   0.8104                  0.1473                   0.9239                  0.0564                   0.1175                  0.1908                 0.7857                0.1107                  0.2773                 0.2005
       kmeans               R2_center_count                   0.8131                  0.1542                   0.9239                  0.0564                   0.1175                  0.1908                 0.7857                0.1107                  0.2773                 0.2005
       kmeans              R3_center_radius                   0.7508                  0.1184                   0.9239                  0.0564                   0.1226                  0.1997                 0.7807                0.1126                  0.2773                 0.2005
       kmeans        R4_center_radius_count                   0.7515                  0.1179                   0.9239                  0.0564                   0.1226                  0.1997                 0.7807                0.1126                  0.2773                 0.2005
       random                  matched_full                   0.5648                  0.1237                   0.6971                  0.0930                   0.3453                  0.3134                 0.6636                0.1519                  0.2773                 0.2005
          raw                R0_raw_samples                   0.9997                  0.0005                   1.0000                  0.0000                   0.0000                  0.0000                 0.7810                0.1191                  1.0000                 0.0000
         tree                  matched_full                   0.5855                  0.0705                   0.7183                  0.0670                   0.2503                  0.2173                 0.7099                0.1606                  0.1213                 0.0653
```

## GB-specific gate

- Paired GB-vs-KMeans runs: 25
- Mean membership AUC delta (GB minus KMeans): -0.0516
- Mean utility accuracy delta (GB minus KMeans): 0.0071
- Fraction meeting the frozen privacy win rule: 0.560
- Fraction showing the predeclared small/high-purity ball leakage pattern: 0.120

## Negative results and failures

Failed configurations: 5. They remain in the append-only JSONL.
All non-winning releases remain in `experiments/results/privacy_leakage_v1.csv`.

## Strongest competing explanation

Any gain may be caused by lossy prototype release, supervised partitioning, or
the number of representatives. The primary decision therefore uses the
same-count KMeans comparator; random, hierarchical, tree, and raw releases are
diagnostic controls rather than weak foils.

## Decision

**HOLD**
