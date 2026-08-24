# Hypotheses

Hypotheses remain falsifiable and specify affected method family, data region,
observable outcome, competing explanation, and decisive experiment.

## Refuted PH-001 — high-dimensional XOR degradation

Targeted replication rejects ambient dimension as the primary driver. Accuracy
gaps do not worsen monotonically from d=2 to d=500.

- Affected family: purity-split original GBC and adaptive split/overlap GBG.
- Proposed region: XOR-like disconnected alternating labels after random
  projection into high ambient dimension.
- Observable: negative held-out accuracy gap under shared preprocessing.
- Competing explanations: RF-specific advantage, one projection, generator
  artifact, untuned purity, and distance concentration.
- Decisive experiment: completed as XOR v1 (140 runs).

## Pre-hypothesis PH-002 — locally interleaved boundary weakness

Original and adaptive spherical GBC may systematically lose locally interleaved
or curved alternating boundaries when mixed labels fall inside the same local
balls; ambient dimension and disconnected class regions alone are insufficient.

- Evidence region: XOR overlap 0.25 across dimensions 2–500 and five seeds.
- Observable: negative held-out accuracy gap against best RF/RBF-SVM/5-NN.
- Current strength: 69/70 individual method/dimension/seed runs negative.
- Independent support: continuous XOR overlap, checkerboard-4, and sector wheels
  with 4/8/12 sectors.
- Counterexamples: Gaussian XOR with well-separated compact clusters is solved;
  checkerboard-6 does not degrade original GBC.
- Missing: real-data analogue, clean-room method, and a mechanism measure
  connecting within-ball mixed labels/boundary curvature to error.
- Status: cross-method and cross-generator replicated observation, still not a
  research hypothesis because the causal statistic is unresolved.
