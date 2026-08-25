# Privacy Anti-GB Test

## Design

The test stays on Adult and Bank Marketing, where the original signal was
strongest. For each GB purity and seed, all competitors use the same number of
released regions. A competitor is eligible only if its utility is within 0.02
of GB; the lowest membership AUC among eligible competitors attacks the claim.

## Result

- Matched conditions: 30
- Mean privacy advantage (best eligible baseline AUC minus GB AUC): -0.0523
- Fraction where GB retains at least 0.03 lower AUC: 0.033
- Failed configurations: 5

Best competing method counts:

```text
               method  cells
               random     12
         hierarchical      8
 knn_local_prototypes      4
hierarchical_complete      2
         kmeans_tuned      2
 hierarchical_average      1
               kmeans      1
```

Purity sensitivity:

```text
                    mean     std
purity_threshold                
0.80              0.0023  0.0135
0.90             -0.0738  0.0570
0.95             -0.0853  0.0709
```

## Interpretation

The anti-GB gate is stricter than the initial KMeans-only comparator. It includes
tuned KMeans, complete/average/ward hierarchy, random matched groups, tree
leaves, farthest-point local prototypes, and a deliberately label-aware oracle
partition. If one of these matches utility with lower leakage, ball geometry is
not necessary for the observed tradeoff.

## Decision

**KILL**
