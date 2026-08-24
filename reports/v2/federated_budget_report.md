# V2 federated budget report

## Claim

Non-IID clients may have different marginal value of granularity under a global
prototype communication budget.

## Evidence

Sixty Digits configurations completed: 5/10/20 clients, Dirichlet α
0.05/0.1/0.3/1.0, five seeds, quantity scaling target 1:5. Every configuration
contains full communication/accuracy/worst-client frontiers for uniform purity,
equal budget, sample-proportional budget, validation risk-value allocation, a
test-leaking observed coordinate oracle and full central data. Nearest prototype,
weighted logistic regression and a small MLP are all reported.

The allocation problem exists: Uniform→observed-oracle mean risk gap is about
1.12 percentage points and remains roughly 1.0–1.3 pp across all α settings.
Marginal values are heterogeneous, though raw variance is small because value is
measured per byte.

## Negative evidence

F5 does not solve the problem:

- nearest-prototype Estimated→observed-oracle mean gap is about 1.56 pp;
- at the same bytes, F5 mean Accuracy advantage over the best uniform/equal/
  proportional baseline is −0.08 pp for nearest, −0.18 pp for logistic and
  −1.33 pp for MLP;
- only roughly 3–8% of comparable points use at most 80% of baseline bytes at
  the same Accuracy tolerance;
- worst-client improvement is near zero for nearest/logistic and negative for
  MLP;
- downstream models materially change conclusions, so selecting the favorable
  server is prohibited.

The observed oracle is coordinate search initialized by observed allocations,
not an exhaustive oracle. It includes the compared allocations so regret is
nonnegative, but it may underestimate the true oracle gap.

## Closest literature

Pending the forced federated novelty audit. Prototype compression, federated
distillation and client-adaptive compression are likely direct adjacent work.

## Collision risk

HIGH until global-budget/client-specific allocation is distinguished from
standard prototype compression.

## Decision

`P1_PROBLEM_METHOD_REJECTED`: a client allocation opportunity is visible on
Digits, but F5's cheap validation marginal value does not close it. Per the gate,
do not run MNIST or Fashion-MNIST.

## Next kill test

No larger dataset. Run the required novelty audit and analyze why validation
client-value rankings fail to match test-coordinate allocations. Only a new,
prevalidated estimator may reopen FED.
