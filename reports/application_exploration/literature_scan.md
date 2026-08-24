# Application novelty scan, 2024-2026

Checked: 2026-08-25. Scope is low-compute granular-ball applications, with
prototype, cluster, tree and coreset mechanisms treated as collision controls.

## Directly occupied application roles

### Anomaly and time-series anomaly

- GBOC/GVDD already uses density-guided granular-ball prototypes and nearest-ball
  anomaly scoring for time-series anomaly detection
  ([AAAI 2026](https://doi.org/10.1609/aaai.v40i30.39722)).
- Granular-ball random-walk anomaly detection directly replaces sample-level
  state transitions with GB-level transitions
  ([Pattern Recognition 2025](https://doi.org/10.1016/j.patcog.2025.111588)).
- Granular-ball subspace fuzzy-neighborhood anomaly detection is also directly
  occupied ([IEEE TFS 2026](https://doi.org/10.1109/TFUZZ.2026.3670429)).

Decision: generic GB anomaly, time-series anomaly and alert scoring are
`REJECT` before implementation.

### Continual, streaming and open-world memory

- Open continual feature selection already maintains a granular-ball knowledge
  base for unknown-class detection and transfer
  ([TKDE 2024](https://doi.org/10.1109/TKDE.2024.3428485)).
- Online group-streaming feature selection with fuzzy-neighborhood GB rough sets
  is directly occupied
  ([Expert Systems with Applications 2024](https://doi.org/10.1016/j.eswa.2024.123778)).
- BallIL uses multi-granularity ball representations as exemplar-free continual
  memory and includes drift estimation
  ([ICLR 2026 submission](https://openreview.net/pdf?id=Cu8Dd4OuXF)).
- Federated open-class learning already transmits and aggregates granular-ball
  knowledge ([Neural Networks 2026](https://doi.org/10.1016/j.neunet.2026.108817)).

Decision: generic GB replay memory, open-world memory, streaming feature
selection and federated GB cache are `REJECT`. A fixed-budget online-state test
was still allowed because it had a measurable local-update systems gate; it
subsequently failed GB attribution.

## Less occupied but high-collision roles

### Cell-level data cleaning

- Conformal Data Cleaning directly targets cell-level error detection and repair
  without granular balls
  ([AISTATS 2024](https://proceedings.mlr.press/v238/jager24a.html)).
- Recent GB label-noise and open-intent work focuses on sample/label selection,
  not numeric cell repair, leaving an application-level gap but no guaranteed GB
  mechanism.

Decision: one cross-fitted matched test was justified. It failed kNN/tree and
same-partition center-only controls, so the role is `REJECT`.

### Batch active learning

- Batch active learning, diversity and coreset selection are mature non-GB
  mechanisms; bilevel data summarization explicitly covers coreset batch active
  learning ([JMLR 2024](https://www.jmlr.org/papers/volume25/21-1132/21-1132.pdf)).
- No direct 2024-2026 granular-ball batch-active-learning title was found in the
  searched primary indexes. This is negative evidence only, not novelty proof.

Decision: a matched GB/KMeans/entropy/k-center test was justified. Its radius
effect failed to transfer beyond Iris, so the role is `REJECT`.

## Gate learned from the round

Recursive 2-means plus centers, medians or prototypes is not by itself a
granular-ball contribution. Every future application must include a same-
partition control that removes radius or ball membership while preserving the
hierarchy and local statistics. A positive result that disappears under this
control is generic hierarchical clustering, not a GB application advance.
