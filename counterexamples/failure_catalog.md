# Failure catalog

Status levels: `observation`, `replicated`, `cross-method`, `research-hypothesis`.

## O-001 — Overlap-driven XOR common weakness

- Status: `cross-method` within one synthetic family; not a research hypothesis.
- Evidence: 140-run XOR v1, dimensions 2/5/10/20/50/100/500,
  overlaps 0.05/0.25, seeds 1/7/21/42/2026, original/adaptive author code,
  and best-of RF/RBF-SVM/5-NN reference.
- Result at overlap 0.25: original mean gap −0.090; adaptive mean gap
  −0.069; 69/70 individual runs have a negative gap.
- Falsified explanation: ambient dimension does not show monotonic degradation;
  d=500 is not systematically worse than d=2.
- Alternative explanations: nearest-center downstream choice, purity threshold,
  synthetic XOR construction, and reference-model selection.
- Required replication: alternate XOR/checkerboard generators, clean-room GBC
  implementation, and a real dataset with alternating/disconnected local labels.

## O-002 — Method-specific split between moons and imbalanced density

- Status: `observation`.
- Evidence: trials 001 and 011.
- Result: adaptive repairs the original moons gap, but adaptive alone degrades on imbalanced density.
- Interpretation: fixed and adaptive rules move failure regions rather than uniformly shrinking them; causal mechanism unverified.

## M-001 — FailureScore denominator pathology

- Status: `replicated` as an arithmetic property; scientific consequence requires policy change.
- Evidence: trial 009 has near-perfect reference accuracy, causing ratios up to 9.33 while absolute GBC accuracy remains near 1.
- Action: require absolute-gap reporting and a minimum reference-loss floor before ratio ranking.
