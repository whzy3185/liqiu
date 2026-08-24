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

## 2026-08-24 — M12 purity-path change point

- Reason: heuristic instability plus `PARTIAL_COLLISION` with generic complexity
  paths/change-point model selection.
- Evidence: 45 nested train/validation/test runs, `m12v1-*`.
- Curvature selects the one-ball Phoneme regime and loses about 0.13 Accuracy.
- Knee damages Banknote and loses up to 0.25 on Sonar.
- Plateau helps Banknote/Phoneme but repeats Ionosphere over-refinement.
- Conclusion: plausible knee definitions disagree across data and seeds. Without
  a derived risk property, “change point” is post-hoc hyperparameter selection.

## 2026-08-24 — M02 local validation risk/cost pruning

- Reason: mechanism failure plus generic cost-complexity/pruning collision.
- Global control v2 helps some datasets but is unstable on Ionosphere/Sonar.
- Local prototype: maximal-purity trees, three-fold cross-fit ensemble,
  bottom-up keep/split validation, two-half stability guard and leaf cost.
- Evidence: 45 runs across Electricity/Phoneme/Ionosphere (`p0lv1-*`,
  `p0lv2-*`). Lowering min local validation from 20 to 5 does not remove held-out
  Accuracy loss; Brier also usually worsens on Phoneme/Ionosphere.
- Conclusion: validation data become too sparse exactly where local refinement
  is needed. Ordinary local pruning is not a reliable H-003 repair.
