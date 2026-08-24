# Counterexample report

## Generator readiness

Twelve deterministic geometry families now pass shape, binary-label, seed
replay, and high-dimensional embedding tests. The shared parameter surface
includes separation, overlap, curvature, manifold width, density ratio,
imbalance ratio, ambient dimension, label-noise type/rate, feature noise, and
outlier rate.

No model failure has yet been recorded. A difficult-looking plot is not a
counterexample; promotion requires repeated experiments across seeds, methods,
and generator families, followed by a real-data check.

## Missing before failure search

- streaming drift generators (covariate, concept, prior, emerging/disappearing
  class);
- validated train/test and scaling protocol shared by granular and classical
  baselines;
- at least five runnable GBC/3WD baselines;
- structural instability and calibration metrics in the search objective.
