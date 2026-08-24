# V2 theory frontier report

## Claim

Heterogeneous regions can create a nonuniform granularity allocation opportunity
that uniform global purity cannot reach at the same risk/resource point.

## Evidence — generation method 1

The first frozen batch completed 120/120 configurations (four families × six
parameter settings × five seeds). Every run has some positive global-threshold
Pareto regret. Mean regret across the 10 global thresholds is approximately:

- Family A: 0.83 percentage point;
- Family B: 1.14 pp;
- Family C: 1.86 pp;
- Family D: 0.73 pp.

The validation-selected risk-budget cut at ε=.01 is close to the test oracle on
average (about 0.03 pp risk regret). Detailed Condition A/B rates are generated
in `v2_theory_frontier_summary.json`.

## Negative evidence / limitations

- Region identity/routing is known. Oracle nonuniform cuts are an existence
  proof, not a deployable algorithm.
- Oracle uses hidden test risk and cannot be reported as a method.
- Only one tree generator has completed; Theory-3 requires two.
- Random configurations are bounded rather than a full factorial design.

## Closest literature

Pending the forced theory collision audit after both generators complete.

## Collision risk

HIGH until separated from cost-complexity pruning, adaptive partitions, rate
distortion and structural-risk minimization.

## Decision

`CONTINUE`: the Uniform→Oracle signal is large enough to justify the frozen
second generator. No P0/P1 label yet.

## Next kill test

Repeat the identical 120 configurations with class-mean-seeded splitting. Apply
Theory-3 only after cross-method aggregation.
