# Failure catalog

Status levels: `observation`, `replicated`, `cross-method`, `research-hypothesis`.

## O-001 — Overlap-driven XOR common weakness

- Status: `provisional`; v1 used nearest-center rather than the author's
  center-distance-minus-radius classifier. Corrected v2 pending.
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

### Independent-generator update

- Alternating v1 adds Gaussian-cluster XOR, checkerboards, and sector wheels
  across five seeds (90 runs).
- Sector wheels with 4/8/12 alternating sectors reproduce negative gaps for
  both methods; checkerboard-4 also reproduces.
- Gaussian XOR at cluster standard deviations 0.10/0.25 is exactly tied for all
  methods/seeds. At 0.40, gaps remain near zero.
- Checkerboard-6 does not reproduce for original GBC.
- Refined boundary: disconnected same-class regions alone are insufficient;
  local interleaving/curvature plus overlap is a better descriptor, but the
  governing geometric statistic remains unknown.

## O-002 — Method-specific split between moons and imbalanced density

- Status: `observation`.
- Evidence: trials 001 and 011.
- Result: adaptive repairs the original moons gap, but adaptive alone degrades on imbalanced density.
- Interpretation: fixed and adaptive rules move failure regions rather than uniformly shrinking them; causal mechanism unverified.

## M-001 — FailureScore denominator pathology

- Status: `replicated` as an arithmetic property; scientific consequence requires policy change.
- Evidence: trial 009 has near-perfect reference accuracy, causing ratios up to 9.33 while absolute GBC accuracy remains near 1.
- Action: require absolute-gap reporting and a minimum reference-loss floor before ratio ranking.

## O-003 — Purity blindness and possible fragmentation signal

- Status: `observation`; causal interpretation unresolved.
- Evidence: 230 XOR/alternating targeted runs with recorded structures.
- Original GBC has zero samples in balls below the configured 0.85 purity
  threshold in all 115 runs, yet held-out gaps reach −0.16.
- Weighted training-ball impurity correlates only moderately with gap
  (Pearson −0.28 overall).
- Ball count correlates −0.34 and mean ball size +0.50 with gap, suggesting
  fragmentation may matter, but family/parameter confounding is not removed.
- Interpretation: purity-stop satisfaction is not evidence that a structure is
  reliable out of sample. Direct boundary/coverage stability measures are needed.
