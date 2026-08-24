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
