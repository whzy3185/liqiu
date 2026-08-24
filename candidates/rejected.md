# Rejected candidates

Rejections are append-only. Record date, candidate, reason, collision evidence,
failed experiment IDs, and any reusable insight.

## 2026-08-24 — M05 Local MDL code-length stop

- Reason: `HIGH_COLLISION`.
- Direct collision: Xian et al., *A Boundary-Aware Non-parametric Granular-Ball
  Classifier Based on Minimum Description Length*, arXiv:2605.11406.
- Additional collision: *Minimum Description Length based Granular-Ball Tree
  Regularization for Spectral Clustering*, arXiv:2605.22410.
- Equivalence risk: both perform local granular-ball model selection with MDL;
  the classifier chooses retain/split/core-boundary explanations.
- Reusable insight: the paper supports replacing heuristic local construction,
  but removes MDL as our candidate novelty.

## 2026-08-24 — M01 confidence-bound purity stop

- Reason: mechanism failure plus `PARTIAL_COLLISION`.
- Evidence: 15 real-data Cheap Test runs, experiment IDs `m01v1-*`, compared
  with identical-seed observed-purity p=0.85 runs.
- Electricity: ~330 extra balls for approximately zero Accuracy change.
- Ionosphere: ~44 extra balls and a substantial Accuracy decrease.
- Phoneme: small mean gain with ~174 extra balls; Banknote/Sonar improve.
- Conclusion: a lower confidence bound is conservatively well-defined but moves
  the system toward the same over-refinement/explosion H-003 identifies. It does
  not reconcile incompatible regimes.
- Reusable insight: finite-sample uncertainty needs a three-way or value/cost
  action, not a uniformly stricter stop rule.
