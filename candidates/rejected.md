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
