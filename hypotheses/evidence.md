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

### Public OpenML exploration

- Ionosphere, Sonar, Banknote, Phoneme and Electricity each ran with five seeds.
- All 25 fixed-purity GBC runs trail the best RF/RBF-SVM/5-NN reference.
- Ionosphere has the largest mean gap (−0.240); Electricity follows (−0.119).
- These are real-data failure observations but not PH-002 confirmation because
  local interleaving/curvature has not been measured on the datasets.

### PH-003 global-purity scan

- 105/105 runs completed across five datasets, three seeds and seven thresholds.
- Phoneme exhibits an under-splitting phase transition between p=0.70 and 0.80.
- Electricity exhibits granule explosion with negligible post-0.80 accuracy gain.
- Ionosphere exhibits non-monotonic accuracy and seed instability after p=0.80.
- Banknote counterexample: greater purity improves accuracy monotonically to 1.0.
- Conclusion: one global setting is not uniformly appropriate; cross-method
  replication was required before promotion.

### H-003 accelerated-GB replication

- A second 105-run scan uses author `gb_accelerate_upload.py` with full-dimensional
  generation and boundary-distance prediction.
- Phoneme again stays at one ball through p=0.70 and jumps to hundreds at p=0.80.
- Electricity again grows from roughly one thousand balls at p=0.80 to roughly
  1700 at p=1.00 for little accuracy gain.
- Banknote favors high purity; Sonar's optimum occurs lower and is seed-sensitive;
  Ionosphere has a different non-monotonic curve from original GBC.
- H-003 is promoted as a cross-method real-data hypothesis. The evidence supports
  adaptive/local stopping as a problem class, not any particular solution.

### H-003 minimal theory construction

- 40/40 runs verify the two-distribution construction at q=.7.
- Separable labels: τ≤.7 gives 1 ball/Accuracy .7; τ>.7 gives 2 balls/Accuracy 1.
- Feature-independent labels: τ≤.7 gives 1 ball/Accuracy .7; τ>.7 produces
  hundreds of balls and Accuracy below .7.
- Proposition 1 formalizes why no global threshold is compatible with both
  regimes. Proposition 2 gives a worst-case local validation sample requirement
  proportional to `1/Δ²`, explaining failed sequential/local controls.

### Global validation negative control

- `m02gv1-*` is invalid: the test matrix was transformed twice with incompatible
  scalers. The 45 records remain for audit but provide no hypothesis evidence.
- Corrected `m02gv2-*` is required before drawing any conclusion.

### Corrected M02 global control

- `m02gv2-*` completes 45 runs with untouched test preprocessing.
- Banknote gains about 0.023 Accuracy; Phoneme gains roughly 0.025–0.051
  depending on λ.
- Electricity λ=0.10 reduces hundreds of balls for near-zero mean Accuracy cost.
- Ionosphere loses about 0.117 on average due to unstable high-purity selection;
  Sonar has one degrading seed.
- Conclusion: risk/cost information is useful, but single-split global validation
  is not reliable. Any M02 continuation needs cross-fit/uncertainty stability.

### M04 global calibration control

- 45 runs select global purity by validation Brier + λ·ball ratio.
- Electricity: Brier improves by about 0.065 and ball count collapses, but
  Accuracy drops about 0.048.
- Banknote and several Phoneme runs improve both probability score and Accuracy.
- Ionosphere has a catastrophic seed; Sonar mostly worsens Brier/Accuracy.
- Conclusion: calibration exposes a real axis of H-003 but cannot be optimized
  alone. Future mechanisms need explicit accuracy, calibration and cost constraints.
