# V2 mechanism prediction report

## Claim

Marginal value of granularity should vary across regions/clients and an estimated
value should rank refinements similarly to hidden task value.

## Evidence

Theory oracle frontiers have nonzero marginal-value variance. Across frozen base
settings, the mean seed-to-seed Spearman rank correlation of regional values is
about 0.40: heterogeneous value exists, but ranking is only moderately stable.

In FED Digits, Uniform→observed-oracle risk gap is positive in every run and
averages 1.12 pp, demonstrating an allocation opportunity. However, validation
risk-value allocation remains about 1.56 pp behind the nearest-prototype observed
oracle and does not beat uniform/equal/proportional allocation at equal bytes.

## Negative evidence

- Theory's known region identity and test oracle are unavailable in practice.
- Estimated ε=.01 cuts have low risk regret but do not consistently save 30%
  resources across families/methods.
- FED marginal-value variance per byte is numerically small and validation ranks
  are not stored strongly enough to claim stable client ordering.
- MLP server behavior is materially worse than nearest/logistic, so downstream
  dependence is unresolved.

## Closest literature

Value allocation is adjacent to tree pruning/SRM/rate-distortion in Theory and
FedProto/adaptive compression/rate-constrained distillation in FED.

## Collision risk

HIGH.

## Decision

The allocation problem is real in THEORY/FED, but the marginal-value estimator
is not validated. No algorithm enters P0.

## Next kill test

On the existing 60 Digits settings, record per-client validation and hidden-test
marginal value vectors and evaluate leave-client-out/seed rank correlation. If
median |rho| < 0.3, reject validation marginal value as the shared mechanism.
