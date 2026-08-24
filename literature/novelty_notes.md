# Novelty notes

Candidate-level collision checks use `CLEAR`, `PARTIAL_COLLISION`,
`HIGH_COLLISION`, or `UNKNOWN`, list the five closest papers when available, and
state both substantive differences and likely reviewer objections.

## H-003 first-pass Novelty Gate — 2026-08-24

Sources: Crossref title search plus the 160-record corpus. This is discovery-level
only; Google Scholar/IEEE/ACM/Springer/ScienceDirect full-text checks remain.

### M01 — confidence-bound purity stop

- NOVELTY_STATUS: `PARTIAL_COLLISION` (no GBC direct collision; generic
  small-sample tree-pruning equivalence).
- Closest: *An Efficient and Adaptive Granular-Ball Generation Method in
  Classification Problem* (10.1109/TNNLS.2022.3203381); *GBG++* (10.1109/TETCI.2024.3359091);
  *Constructing Three-Way Decision With Fuzzy Granular-Ball Rough Sets Based on
  Uncertainty Invariance* (10.1109/TFUZZ.2025.3536564).
- Difference to verify: finite-sample lower confidence guarantee for local class
  proportion rather than heuristic/adaptive observed purity.
- Reviewer objection: this may be a textbook binomial interval applied to GBC,
  with novelty limited to replacing a threshold.
- Adjacent closest work: *Small Sample Decision Tree Pruning*
  (10.1016/B978-1-55860-335-6.50048-9) and probabilistic/cost-sensitive tree
  pruning. Cheap Test is permitted only as a kill test, not novelty evidence.

### M02 — cross-fitted local risk/cost stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- Closest: adaptive GBG and GBG++; no direct validation-risk title found.
- Difference to verify: out-of-sample local action selection under explicit ball
  cost, not training-purity gain.
- Reviewer objection: equivalent to ordinary cost-complexity pruning or local
  cross-validation with GBC terminology.
- Adjacent collision class: CART cost-complexity and probabilistic pruning; a
  GBC version needs a mechanism/theory not reducible to tree pruning.

### M03 — perturbation stability stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- Closest: *GBG++: A Fast and Stable Granular Ball Generation Method for
  Classification*; *A novel self-adaptive fuzzy concept-cognitive learning based
  granular-ball splitting* (10.1007/s13042-025-02964-8).
- Difference to verify: stability is measured under data perturbations and is the
  stopping objective, rather than an empirical descriptor/name.
- Reviewer objection: “stable” GBG is already occupied; likely incremental.

### M04 — calibration-aware stop

- NOVELTY_STATUS: `PARTIAL_COLLISION` (no direct GBC collision).
- Closest: uncertainty-invariance 3WD and fuzzy granular-ball classifiers.
- Difference to verify: held-out proper scoring rule/calibration controls split.
- Reviewer objection: ECE-based tuning is statistically weak and may overfit.
- Adjacent collision class: probability-estimation trees, including *Decision
  Tree with Better Class Probability Estimation* (10.1142/S0218001409007296)
  and improved class-probability tree estimators. A GBC result must connect
  granulation decisions to proper-score/risk guarantees, not merely recalibrate.

### M08 — value-of-information split

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- No exact granular-ball VOI result found in arXiv/DBLP/Crossref queries.
- Adjacent collision class: cost-sensitive decision trees and classical value of
  information decision theory.
- Reviewer objection: generic split-benefit divided by cost, renamed for GBC.

### M12 — change-point purity-cost stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- No exact granular-ball change-point result found.
- Adjacent closest work: stochastic-complexity change-point detection and
  complexity regularization paths.
- Reviewer objection: offline hyperparameter knee detection rather than a new
  granulation mechanism; nested validation is required to avoid benchmark leak.

### M05 — local MDL stop

- NOVELTY_STATUS: `HIGH_COLLISION` → rejected.
- Direct collision: *A Boundary-Aware Non-parametric Granular-Ball Classifier
  Based on Minimum Description Length* (arXiv:2605.11406). It performs local MDL
  selection among single-ball, two-ball and core-boundary models.
- Additional collision: *Minimum Description Length based Granular-Ball Tree
  Regularization for Spectral Clustering* (arXiv:2605.22410).
- Reviewer objection is decisive: local MDL granular-ball construction is
  already explicit, current, and classification-specific.

### M06 — Pareto multi-objective stop

- NOVELTY_STATUS: `PARTIAL_COLLISION`.
- Closest: *MOGBC: Multi-objective Driven Granular Ball Clustering*
  (10.1007/978-3-031-92747-8_25).
- Reviewer objection: direct task migration from clustering to classification.

## Gate decision

No candidate is `CLEAR`. M05 is rejected. Deeper checks prioritize
M01/M12/M04/M02/M08. M03 and M06 are deprioritized because collision risk is
already material. Semantic Scholar was rate-limited; DBLP exposed M05.

## Candidate 6 theory gate — 2026-08-24

- NOVELTY_STATUS: `UNKNOWN`; no direct title-level collision found in the
  162-paper corpus, DBLP, or Crossref queries for granular-ball purity threshold
  theory, complexity bounds, or sample complexity.
- Closest mechanisms: adaptive GBG, GBG++, self-adaptive granular-ball splitting,
  and MDL-GBC local model selection.
- Difference: Proposition 1 is an incompatibility result for any global purity
  threshold across two equal-root-purity regimes; Proposition 2 quantifies why
  distribution-free local validation is impractical for small gains.
- Potential reviewer objection: the two-distribution construction and Hoeffding
  calculation may be mathematically correct but too elementary. A nontrivial
  recursive ball-count/risk lower bound or selective-partition result is needed.
- Gate decision: retain as P1 theory track; do not claim `CLEAR`.

## Candidate 8 component-benchmark gate — 2026-08-24

- NOVELTY_STATUS: `UNKNOWN`; DBLP/Crossref title queries found no direct
  granular-ball component-controlled benchmark, radius-vs-center decision audit,
  or reproducibility study.
- Closest work consists of individual GBC classifiers, natural-neighbor GBC,
  GBKTSVC/GBTSVM and 3WC-GBNRS++; these propose methods rather than isolate
  representation/generation/decision components under fixed structures.
- Difference: paired experiments change only the decision distance, retain the
  same 230 configurations, and quantify failure-sign/ranking changes; author code
  consistency and invalid-result retention are part of the artifact.
- Potential reviewer objection: this is engineering/reproduction rather than a
  research mechanism. It needs independent implementations and more decision
  rules to justify a standalone benchmark contribution.
- Gate decision: retain as P1 artifact/analysis line, not an algorithm paper.
