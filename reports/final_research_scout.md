# 1. Executive Summary

This CPU-first scout completed the literature boundary, Privacy Leakage,
Cloud Auditing, Multi-Auditor, Secure-Aggregation compression, ranking, and the
required Anti-GB attack. Differentially Private GB was correctly not run because
its prerequisite failed; image privacy was optional and deferred.

The initial Privacy Leakage test produced a tempting result: at equal
representative count, GB membership AUC was on average 0.0516 lower than KMeans
while utility was 0.0071 higher. It was not stable enough to `GO` (56% frozen
wins), and the Anti-GB test then falsified GB necessity. All evaluated directions
are now `KILL`.

**Final decision: ABANDON GB PRIVACY/AUDIT LINE.**

# 2. Literature Boundary

The closest direct work is the 2025 GrBFL preprint, which empirically makes
gradient-based image reconstruction harder by replacing pixels with granular
rectangle graphs. This is empirical information loss, not differential privacy,
information-theoretic privacy, or cryptographic confidentiality. A 2026 Neural
Networks paper uploads granular-ball knowledge in federated open-intent
classification but does not systematically attack released tabular summaries.

No direct hit was found for formal GB+DP, cloud-storage public auditing,
multi-auditor storage auditing, or GB as pre-HE/MPC compression. These scoped
gaps are real enough to test, but absence of prior work did not imply GB value.
Adjacent three-way DP, federated cloud scheduling, MPC/FHE feature selection,
microaggregation, and generic prototype compression set the actual baseline bar.

# 3. Cheap Test Results

| Direction | Most informative number | Decision |
|---|---|---|
| Privacy Leakage | Initial GB-KMeans AUC delta -0.0516; Anti-GB advantage -0.0523; retained wins 0.033 | KILL |
| Cloud Auditing | Structured detection gain over strongest non-GB -0.0074 across 90 cells | KILL |
| Multi-Auditor | Accuracy gain over strongest non-GB -0.0196 across 120 conditions | KILL |
| Secure Aggregation | GB-KMeans accuracy -0.0032; compression gate only 0.044 | KILL |
| DP Granular Ball | Not run because Privacy/Anti-GB prerequisite failed | KILL by gate |

The executed scout added 70 immutable experiment records: 60 successful runs
and 10 retained loader/boundary failures, each with Git state, config hash,
runtime, and memory.

# 4. Negative Results

- GB privacy gains were dataset dependent: Adult and Bank were favorable,
  Covertype was near-neutral, and German Credit favored KMeans.
- Radius/count/purity did not produce a stable GB-specific leakage mechanism.
- Cloud GB grouping did not beat the per-cell strongest direct risk, anomaly,
  KMeans, or tree policy under structured corruption.
- GB multi-auditor trust was weaker than weighted majority and did not improve
  any matched condition by at least 0.01.
- GB compression averaged `m/n=0.2094` and 0.0327 raw-accuracy loss; the target
  gate was `m/n<=0.1` and loss <=0.02.
- Two deterministic schema/one-group failures were fixed under new experiment
  IDs; the original ten failure records remain auditable.

# 5. Why Granular Ball?

Current evidence does not establish a necessary GB property. Initial privacy
separation from KMeans was real but not specific: other same-count partitions
could keep utility while leaking less. Audit and trust gains tracked ordinary
risk stratification. Communication savings tracked prototype count, where GB
was neither smaller nor more accurate than matched KMeans.

# 6. Strongest Competing Explanation

Lossy aggregation, label-aware partitioning, and risk stratification explain the
observed results without ball geometry. The Anti-GB test supports this directly:
random matched groups were the strongest eligible privacy competitor in 12/30
cells, ordinary hierarchy in 11/30, and local/tuned prototypes in the remainder.

# 7. Recommended Direction

Do not continue a positive "GB for privacy/auditing" paper. If this work is
retained, its honest form is a negative benchmark: granular summaries are not a
privacy mechanism, and same-budget controls are mandatory. A better technical
direction is method-agnostic privacy-aware microaggregation or robust audit
sampling, without requiring GB branding.

# 8. Next 20 Experiments

Only run these if a negative-result/benchmark paper is deliberately pursued:

1. Freeze a confirmation pool before any new tuning.
2. Replace the in-dataset membership attack learner with independent shadow datasets.
3. Match released byte count, not only representative count.
4. Match partition entropy and group-size distribution.
5. Add class-aware KMeans as a non-oracle baseline.
6. Add constrained microaggregation with minimum group size.
7. Evaluate population/property inference from counts and purity.
8. Evaluate reconstruction of rare categorical combinations.
9. Measure singleton and near-singleton disclosure explicitly.
10. Derive sensitivity of center/radius/count under bounded features.
11. Prove a counterexample where purity splitting increases membership leakage.
12. Sweep corruption locality while holding marginal risk fixed.
13. Add a minimax audit floor to every adaptive policy.
14. Separate risk-model error from sampling-policy error.
15. Hold out auditor histories when learning competence.
16. Vary adaptive-malicious switch time independently of collusion.
17. Compare against robust truth-discovery models beyond Dawid-Skene.
18. Sweep client heterogeneity while matching total prototypes globally.
19. Serialize prototypes to measure actual bytes and packing overhead.
20. Reproduce all surviving negative claims in an independent implementation.

# 9. Paper Hypothesis

At matched utility and release/audit/communication budget, granular-ball
representations do not provide a stable privacy, audit-detection, trust, or
compression advantage over ordinary adaptive partitions.

# 10. Decision

**ABANDON GB PRIVACY/AUDIT LINE**

