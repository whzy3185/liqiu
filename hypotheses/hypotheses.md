# Hypotheses

Hypotheses remain falsifiable and specify affected method family, data region,
observable outcome, competing explanation, and decisive experiment.

## Pre-hypothesis PH-001 — high-dimensional XOR degradation

Not promoted to a research hypothesis. Campaign v1 suggests both original and
adaptive GBC trail random forest on one d=100 XOR parameterization.

- Affected family: purity-split original GBC and adaptive split/overlap GBG.
- Proposed region: XOR-like disconnected alternating labels after random
  projection into high ambient dimension.
- Observable: negative held-out accuracy gap under shared preprocessing.
- Competing explanations: RF-specific advantage, one projection, generator
  artifact, untuned purity, and distance concentration.
- Decisive experiment: dimensions 2/5/10/20/50/100/500, rotation/projection and
  overlap variants, seeds 1/7/21/42/2026, with RF/SVM/KNN references.
