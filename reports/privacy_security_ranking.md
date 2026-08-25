# Unified Cheap-Test Ranking

The weighted score is
`0.30 empirical + 0.25 GB-specificity + 0.20 novelty + 0.15 mechanism + 0.10 reproducibility`.
Paper extensibility is reported but not included in the supplied formula.

| Rank | Direction | Total | Final gate |
|---:|---|---:|---|
| 1 | Privacy Leakage | 2.65 | KILL after Anti-GB |
| 2 | Cloud Auditing | 2.15 | KILL |
| 2 | Multi-Auditor | 2.15 | KILL |
| 4 | Secure Aggregation | 1.95 | KILL |
| 5 | DP Granular Ball | 1.40 | KILL by prerequisite |

Privacy Leakage ranked first after the initial KMeans-only gate, so it received
the required Anti-GB test. That test reversed the provisional `HOLD`: once
random matched partitions, multiple hierarchical linkages, farthest-point local
prototypes, trees, tuned KMeans, and a label-aware oracle were eligible, the GB
privacy advantage was negative on average and survived in only 1/30 conditions.

No direction enters mechanism expansion or a real cryptographic benchmark.

