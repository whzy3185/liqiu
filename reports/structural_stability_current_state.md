# Structural-Stability Current-State Audit

Branch: `exp/granular-ball-structural-stability`, created from the completed
privacy-refinement head `df56e50`.  The A3 real-transfer line remains
`KILL_A_REAL_TRANSFER`; its synthetic-only family is eligible only as a
controlled structural stress family.

## Reusable implementations

| implementation | source status | construction | decision available | relevance |
| --- | --- | --- | --- | --- |
| `studies.risk_granularity.GranulationTree` | repository clean-room | recursive binary KMeans or class-means split; reusable purity cuts | nearest-center/radius-aware probability | exposes hierarchy, cut membership, purity, radius, and depth |
| `baselines.gbc.GranularBallClassifier` | clean-room audited against original GBC structure smoke | impurity split into number-of-labels KMeans children | boundary-distance native rule; centers/labels exposed | supplies an original-style multiway generator |
| `ConfidenceBoundGranularBallClassifier` | existing repository cheap-test control, not an author method claim | same construction with Wilson-bound stopping | same as original | usable only as an explicitly labelled stop-rule control |
| upstream original/adaptive adapters | author-account code audited but not vendored | original and adaptive paper paths | structure smoke only | unsuitable for the first full matrix until a licensed reproducible wrapper is available |

GBG++ and LDGBG are documented in `baselines/upstream_registry.csv` as paper
verified but without a reliable public implementation.  They are not silently
substituted or presented as author-code reproductions.

## Existing perturbation and structure assets

- `counterexamples.generators` and core-noise runners already provide controlled
  clean, overlap, density and label-noise families with fixed clean test data.
- The core label-noise report contains paired ball count, fragmentation, purity
  and predictive-risk evidence, but it does **not** compare partitions over
  common samples or fixed-test prediction agreement.  It is background, not
  direct structural-stability evidence.
- `GranulationTree.cut()` exposes leaf membership and hierarchy; the A3 release
  code records centers, radii, purity, ball sizes and refinement depth.  These
  support established partition comparisons and descriptive drift statistics.
- Existing application drift, active-learning, failure-slice and privacy
  results are rejected/closed application lines.  They must not be rerun or
  reframed as a stability result.

## Directly computable v1 measurements

For two fitted structures on shared training samples: Adjusted Rand Index
(ARI), Normalized Mutual Information (NMI), and Variation of Information (VI)
are directly computable from leaf assignments.  Ball count, size, singleton,
radius, purity and (for `GranulationTree`) depth are also directly available.
All four first-round implementations can use the same nearest-center decision
on a fixed held-out test set.

## Non-repeat and scope restrictions

- Do not reopen A3 real-data membership discovery, B0, rejected applications,
  or a new granular-ball generator.
- Do not use accuracy alone as stability evidence; prediction agreement is
  required.
- Do not call clean-room implementations author code, and do not infer
  GBG++/LDGBG behavior without runnable audited code.
- Do not create a composite stability score or a tree-edit distance in v1.
