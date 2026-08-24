# V2 theory frontier report

## Claim

Heterogeneous regions can create a nonuniform granularity allocation opportunity
that uniform global purity cannot reach at the same risk/resource point.

## Evidence — two generation methods

Both frozen batches completed: 240/240 configurations, four families, five seeds,
KMeans and class-mean-seeded trees. Every family/method group has positive global
Pareto regret in 100% of runs, so Theory-3 Condition C passes.

Mean global-threshold regret ranges from 0.73–1.86 pp for KMeans trees and
1.60–2.45 pp for class-mean trees. Oracle Condition B occurs in 80–100% of runs
for most groups; the lowest group is still 56.7%.

For KMeans, mean regret across the 10 global thresholds is approximately:

- Family A: 0.83 percentage point;
- Family B: 1.14 pp;
- Family C: 1.86 pp;
- Family D: 0.73 pp.

The validation-selected risk-budget cut at ε=.01 is close to the test oracle in
risk (roughly 0–0.11 pp mean regret), but ≥30% resource savings occurs
inconsistently: only 3.3%–93.3% depending on family/method. Thus the allocation
problem is stable while the simple estimated cut is not uniformly solved.

Oracle frontier transitions provide an empirical marginal-value distribution;
variance and seed rank stability are reported separately. These are oracle
diagnostics, not a deployable value estimator.

## Negative evidence / limitations

- Region identity/routing is known. Oracle nonuniform cuts are an existence
  proof, not a deployable algorithm.
- Oracle uses hidden test risk and cannot be reported as a method.
- Random configurations are bounded rather than a full factorial design.
- Estimated allocation assumes the heterogeneous region partition is known.

## Closest literature

The forced theory collision audit is now required before any theorem packaging.

## Collision risk

HIGH until separated from cost-complexity pruning, adaptive partitions, rate
distortion and structural-risk minimization.

## Decision

`P1_PENDING_COLLISION`: Theory-3 passes via Condition C across four families and
two methods. It is not P0 because practical region discovery and novelty are not
established.

## Next kill test

Run the forced adaptive-partition/CART/rate-distortion collision audit. In
parallel, run the FED Digits Cheap Test as prescribed. Do not start GNN yet.
