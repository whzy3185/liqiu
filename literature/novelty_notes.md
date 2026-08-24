# Novelty notes

Candidate-level collision checks use `CLEAR`, `PARTIAL_COLLISION`,
`HIGH_COLLISION`, or `UNKNOWN`, list the five closest papers when available, and
state both substantive differences and likely reviewer objections.

## H-003 first-pass Novelty Gate — 2026-08-24

Sources: Crossref title search plus the 160-record corpus. This is discovery-level
only; Google Scholar/IEEE/ACM/Springer/ScienceDirect full-text checks remain.

### M01 — confidence-bound purity stop

- NOVELTY_STATUS: `UNKNOWN` (no title-level direct collision).
- Closest: *An Efficient and Adaptive Granular-Ball Generation Method in
  Classification Problem* (10.1109/TNNLS.2022.3203381); *GBG++* (10.1109/TETCI.2024.3359091);
  *Constructing Three-Way Decision With Fuzzy Granular-Ball Rough Sets Based on
  Uncertainty Invariance* (10.1109/TFUZZ.2025.3536564).
- Difference to verify: finite-sample lower confidence guarantee for local class
  proportion rather than heuristic/adaptive observed purity.
- Reviewer objection: this may be a textbook binomial interval applied to GBC,
  with novelty limited to replacing a threshold.

### M02 — cross-fitted local risk/cost stop

- NOVELTY_STATUS: `UNKNOWN`.
- Closest: adaptive GBG and GBG++; no direct validation-risk title found.
- Difference to verify: out-of-sample local action selection under explicit ball
  cost, not training-purity gain.
- Reviewer objection: equivalent to ordinary cost-complexity pruning or local
  cross-validation with GBC terminology.

### M03 — perturbation stability stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- Closest: *GBG++: A Fast and Stable Granular Ball Generation Method for
  Classification*; *A novel self-adaptive fuzzy concept-cognitive learning based
  granular-ball splitting* (10.1007/s13042-025-02964-8).
- Difference to verify: stability is measured under data perturbations and is the
  stopping objective, rather than an empirical descriptor/name.
- Reviewer objection: “stable” GBG is already occupied; likely incremental.

### M04 — calibration-aware stop

- NOVELTY_STATUS: `UNKNOWN` (no direct calibration/splitting title found).
- Closest: uncertainty-invariance 3WD and fuzzy granular-ball classifiers.
- Difference to verify: held-out proper scoring rule/calibration controls split.
- Reviewer objection: ECE-based tuning is statistically weak and may overfit.

### M05 — local MDL stop

- NOVELTY_STATUS: `UNKNOWN` (no granular-ball MDL title collision found).
- Closest: general MDL literature; GBG++; multi-objective granular-ball methods.
- Difference to verify: a derived local code for features, labels and ball count
  whose split decision explains the observed phase regimes.
- Reviewer objection: arbitrary coding choices can recreate a hand-tuned penalty.

### M06 — Pareto multi-objective stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- Closest: *MOGBC: Multi-objective Driven Granular Ball Clustering*
  (10.1007/978-3-031-92747-8_25).
- Reviewer objection: direct task migration from clustering to classification.

## Gate decision

No candidate is `CLEAR`. Deeper checks prioritize M05/M01/M12/M04/M02. M03 and
M06 are deprioritized because collision risk is already material.
