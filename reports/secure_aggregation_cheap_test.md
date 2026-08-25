# Secure Aggregation Cheap Test E

## Scope

This phase tests information compression only. Communication operations and
ciphertext counts are estimates; no cryptographic privacy claim is made.
KMeans and microclusters use the same per-client prototype count as GB.

## Mean results

```text
       method  accuracy  accuracy_drop_vs_raw  m_over_n  communication_bytes
granular_ball    0.7656                0.0327    0.2094          192160.1778
       kmeans    0.7687                0.0295    0.2094          192160.1778
 microcluster    0.7673                0.0309    0.2035          185993.6000
          raw    0.7982                0.0000    1.0000          742234.6667
```

## Gates

- Paired GB-vs-KMeans runs: 45
- Mean accuracy gain (GB minus KMeans): -0.0032
- Fraction with at least +0.01 GB accuracy gain: 0.311
- Fraction meeting `m/n <= 0.1` and raw-accuracy drop <= 0.02: 0.044
- Mean GB `m/n`: 0.2094
- Mean GB accuracy drop versus raw: 0.0327

Real HE/MPC implementation is permitted only if both the compression gate and
the GB-specific comparator gate survive. Failed configurations: 0.

## Decision

**KILL**
