# Cloud Auditing Cheap Test C

## Scope

Synthetic clouds contain 10,000 and 100,000 blocks. Every method is evaluated
at the same audited-block budget. The cryptographic PDP/PoR proof is intentionally
out of scope; this test asks only whether risk grouping improves sampling.

## Mean results

```text
     scenario          method  detection_probability  corruption_recall  time_to_first_detection  worst_case_miss_rate
  adversarial   anomaly_score                 0.2778             0.0011                 238.2967                1.0000
  adversarial  gb_center_only                 0.5922             0.0047                 132.8556                0.9998
  adversarial    gb_three_way                 0.4244             0.0023                 191.7222                1.0000
  adversarial   granular_ball                 0.6644             0.0055                 109.1200                0.9995
  adversarial    kmeans_group                 0.6233             0.0053                 118.2411                0.9991
  adversarial      risk_score                 0.0200             0.0000                 327.8856                1.0000
  adversarial  tree_partition                 0.0244             0.0000                 327.8789                1.0000
  adversarial         uniform                 0.7500             0.0095                  76.1511                0.9978
  adversarial weighted_random                 0.6289             0.0050                 111.1967                0.9995
    clustered   anomaly_score                 0.7678             0.0096                  77.4567                0.9986
    clustered  gb_center_only                 0.7667             0.0094                  78.6689                0.9980
    clustered    gb_three_way                 0.7900             0.0099                  74.0267                0.9982
    clustered   granular_ball                 0.7844             0.0098                  74.5022                0.9979
    clustered    kmeans_group                 0.7578             0.0093                  77.6389                0.9981
    clustered      risk_score                 0.7656             0.0094                  76.3700                0.9980
    clustered  tree_partition                 0.7700             0.0091                  74.3811                0.9982
    clustered         uniform                 0.7622             0.0095                  76.0733                0.9974
    clustered weighted_random                 0.7478             0.0094                  79.1044                0.9981
cold_targeted   anomaly_score                 0.7689             0.0094                  70.8989                0.9978
cold_targeted  gb_center_only                 0.7922             0.0107                  69.5667                0.9972
cold_targeted    gb_three_way                 0.8056             0.0121                  64.4800                0.9965
cold_targeted   granular_ball                 0.7911             0.0106                  66.3711                0.9978
cold_targeted    kmeans_group                 0.7989             0.0111                  67.2189                0.9974
cold_targeted      risk_score                 0.7956             0.0103                  73.8478                0.9976
cold_targeted  tree_partition                 0.7956             0.0105                  71.4333                0.9972
cold_targeted         uniform                 0.7733             0.0092                  74.3100                0.9976
cold_targeted weighted_random                 0.7922             0.0104                  71.1667                0.9979
 hot_targeted   anomaly_score                 0.7367             0.0087                  78.4511                0.9979
 hot_targeted  gb_center_only                 0.7811             0.0098                  76.8811                0.9975
 hot_targeted    gb_three_way                 0.7589             0.0088                  82.2600                0.9986
 hot_targeted   granular_ball                 0.7722             0.0095                  73.6333                0.9978
 hot_targeted    kmeans_group                 0.7267             0.0086                  79.4022                0.9986
 hot_targeted      risk_score                 0.7589             0.0091                  78.5533                0.9977
 hot_targeted  tree_partition                 0.7422             0.0088                  78.3756                0.9978
 hot_targeted         uniform                 0.7700             0.0094                  76.2800                0.9979
 hot_targeted weighted_random                 0.7400             0.0085                  82.1978                0.9987
      uniform   anomaly_score                 0.7378             0.0093                  75.9978                0.9982
      uniform  gb_center_only                 0.7556             0.0092                  77.9756                0.9982
      uniform    gb_three_way                 0.7467             0.0092                  75.6733                0.9979
      uniform   granular_ball                 0.7544             0.0093                  76.9789                0.9982
      uniform    kmeans_group                 0.7444             0.0086                  81.1978                0.9985
      uniform      risk_score                 0.7522             0.0091                  77.8067                0.9985
      uniform  tree_partition                 0.7589             0.0096                  76.2333                0.9978
      uniform         uniform                 0.7822             0.0094                  73.0911                0.9981
      uniform weighted_random                 0.7522             0.0091                  78.4689                0.9977
```

## GB-specific gate

- Paired budget/scenario/seed/size cells: 150
- Structured-corruption cells: 90
- Mean structured detection gain over the strongest non-GB baseline: -0.0074
- Structured cells with at least +0.03 detection gain: 0.256
- Structured non-loss fraction: 0.700
- Mean policy-aware adversarial gain: -0.0100

The strongest baseline is selected per matched cell from direct risk score,
weighted sampling, anomaly score, matched KMeans groups, and matched tree
partitions. Uniform sampling is reported but cannot establish a GB contribution.

## Negative results and failures

Failed configurations: 0. All per-seed results, including losses,
remain in `cloud_auditing/results.csv` and the append-only experiment JSONL.

## Decision

**KILL**
