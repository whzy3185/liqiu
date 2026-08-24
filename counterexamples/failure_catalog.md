# Failure catalog

Status levels: `observation`, `replicated`, `cross-method`, `research-hypothesis`.

## O-001 — Overlap-driven XOR common weakness

- Status: `cross-method`, `cross-generator`; no real-data replication yet.
- Corrected evidence: v2 uses the author's center-distance-minus-mean-radius
  classifier and a clean-room implementation verified against author code.
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

### Corrected v2 effect

- XOR overlap 0.25: original/adaptive mean gaps −0.038/−0.038; 65/70 runs
  negative. V1 overstated the effect (−0.090/−0.069).
- Sector wheels 4/8/12: all original runs and 14/15 adaptive runs negative;
  method mean gaps range from −0.031 to −0.058.
- Checkerboard-4: original/adaptive −0.024/−0.046.
- The effect survives faithful boundary-distance classification but is materially
  smaller; v2 supersedes v1 for all classifier claims.

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
- Evidence: 230 corrected-v2 XOR/alternating runs with recorded structures.
- Original GBC has zero samples in balls below the configured 0.85 purity
  threshold in all 115 runs, yet held-out gaps reach −0.16.
- Weighted training-ball impurity correlates moderately with gap (Pearson −0.30
  overall; −0.42 for original).
- Ball count/mean size correlations shrink to −0.22/+0.32 under faithful
  boundary-distance prediction, weakening the earlier fragmentation story.
- Interpretation: purity-stop satisfaction is not evidence that a structure is
  reliable out of sample. Direct boundary/coverage stability measures are needed.
