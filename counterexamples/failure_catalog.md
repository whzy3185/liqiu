# Failure catalog

Status levels: `observation`, `replicated`, `cross-method`, `research-hypothesis`.

## O-001 — High-dimensional XOR common weakness

- Status: `observation` (cross-method within one generator/parameter draw; not yet `cross-method` catalog status)
- Evidence: campaign v1 trial 003, experiments `fsv1-t003-*`, seeds 1/7/21.
- Result: original gap −0.069; adaptive gap −0.050 versus random forest.
- Alternative explanations: axis/projection interaction, reference inductive bias, hyperparameter mismatch, single generator draw.
- Required replication: dimension/overlap grid, rotated XOR, five seeds, additional references.

## O-002 — Method-specific split between moons and imbalanced density

- Status: `observation`.
- Evidence: trials 001 and 011.
- Result: adaptive repairs the original moons gap, but adaptive alone degrades on imbalanced density.
- Interpretation: fixed and adaptive rules move failure regions rather than uniformly shrinking them; causal mechanism unverified.

## M-001 — FailureScore denominator pathology

- Status: `replicated` as an arithmetic property; scientific consequence requires policy change.
- Evidence: trial 009 has near-perfect reference accuracy, causing ratios up to 9.33 while absolute GBC accuracy remains near 1.
- Action: require absolute-gap reporting and a minimum reference-loss floor before ratio ranking.
