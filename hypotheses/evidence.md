# Evidence ledger

Every supporting and contradicting result is linked by experiment ID or primary
source. Contradictory evidence is never omitted from an aggregate conclusion.

## PH-001 evidence ledger

- Supporting: `fsv1-t003-original-*` mean gap −0.069; mean failure ratio 1.46.
- Supporting: `fsv1-t003-adaptive-*` mean gap −0.050; mean failure ratio 1.33.
- Weakening: only one generator parameterization and three seeds.
- Weakening: no SVM/KNN reference and no dimension curve yet.
- Related counterevidence: adaptive GBG outperforms the RF reference on d=100
  moons trial 001, so high dimension alone is not a sufficient failure condition.
- Status: pre-hypothesis; targeted replication required.

### XOR v1 update

- PH-001 is refuted: no monotonic dimension effect across d=2–500.
- At overlap 0.05, mean gaps are −0.025 (original) and −0.035 (adaptive).
- At overlap 0.25, mean gaps are −0.090 (original) and −0.069 (adaptive).
- PH-002 replaces the dimensional explanation with an overlap-driven one.
- Counterevidence retained: adaptive at d=50, overlap 0.25, seed 2026 leads the
  best reference by +0.013, so the effect is strong but not universal.

### Alternating v1 update

- Sector wheel mean gaps (original/adaptive): sectors 4 −0.047/−0.070;
  sectors 8 −0.068/−0.088; sectors 12 −0.056/−0.088.
- Checkerboard-4 mean gaps: −0.053/−0.077.
- Gaussian XOR with compact clusters: zero gap at standard deviations 0.10 and
  0.25 for all 20 method/seed combinations per setting.
- Checkerboard-6: original mean gap +0.012, adaptive −0.026.
- Interpretation: alternation count alone is not monotone; within-ball label
  mixing, curvature, and local scale need to be measured directly.

### Mechanism-signal audit

- V1 used nearest-center prediction and is deprecated for official-classifier
  claims. Corrected v2 uses center distance minus mean radius.
- Across 230 v2 runs, weighted ball impurity vs accuracy gap has Pearson
  correlation −0.30 overall and −0.42 for original; it remains insufficient.
- Granule count vs gap is −0.22 and mean ball size vs gap is +0.32, weakening
  the initial fragmentation explanation.
- Original GBC's below-threshold uncertainty ratio is identically zero in all
  115 targeted runs despite held-out failures. Purity-based stopping is therefore
  blind to these observed generalization gaps under the current protocol.

### Corrected classifier replication

- Clean-room original GBC matches author code on ball sizes and 43 fixed
  boundary-distance predictions.
- XOR overlap 0.25 corrected gaps: −0.038 original, −0.038 adaptive; 65/70
  negative individual runs.
- Sector-wheel corrected gaps remain negative in 29/30 runs across both methods.
- V1 effect sizes were inflated by nearest-center prediction and are retained
  only as downstream-sensitivity evidence.
