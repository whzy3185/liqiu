# Resource / Risk-Constrained Granularity — analysis round report

# Experiment status

| Line | Configs | Seeds | Datasets/families | Methods |
|---|---:|---:|---|---|
| Theory | 240 | 5 | 4 heterogeneous families, 24 frozen settings | global purity, test-oracle nonuniform, validation risk-budget; KMeans and class-mean trees |
| Federated | 60 | 5 | Digits; clients 5/10/20; α .05/.1/.3/1.0 | full, uniform, equal, proportional, estimated risk-value, observed coordinate oracle; nearest/logistic/MLP |
| GNN | 132 recorded / 99 valid | 3 | Cora, Citeseer, PubMed | full, random, heavy-edge, clean-room adaptive/fixed GBGC, CPU GCN |
| Semantic codebook | 0 | 0 | not run | rejected for this round |

All 432 second-round records are append-only and tagged by study. The 33 invalid
Citeseer records remain in JSONL and are superseded by new IDs after the loader
fix. The branch is `exp/risk-granularity-v2` from trusted commit `5ea8541`.

# Theory

- Global-threshold Pareto regret is positive in 100% of runs for all four
  families and both tree generators.
- Mean regret ranges 0.73–2.45 pp across family/method groups.
- Oracle nonuniform cuts pass Condition A in 56.7–96.7% and Condition B in
  56.7–100% of runs depending on group.
- Validation risk-budget ε=.01 has approximately 0–0.11 pp mean oracle risk
  regret, but ≥30% resource saving is unstable (3.3–93.3% by group).
- Theory-3 passes Condition C, but the collision audit finds strong equivalence
  to CART/cost-complexity, optimal TSVQ pruning, adaptive partitions, SRM and
  rate-distortion. Status: `P1_APPLICATION_EXPLANATION`, not standalone theory.

# Federated

- Uniform→observed-oracle mean risk gap: **1.12 pp**; positive in all 60 runs.
- Estimated→observed-oracle nearest-prototype mean gap: **1.56 pp**.
- Same-byte Accuracy advantage of F5 versus best uniform/equal/proportional:
  −0.08 pp nearest, −0.18 pp logistic, −1.33 pp MLP.
- Mean worst-client gain is near zero for nearest/logistic and negative for MLP.
- Same-Accuracy bytes ≤80% occurs only about 3–8% of comparable points.
- F5 fails A/B/C on Digits; MNIST/Fashion-MNIST are not run. Status:
  `P1_PROBLEM_METHOD_REJECTED`.

# GNN

- Adaptive clean-room GBGC is node-risk Pareto-nondominated in 9/9 valid
  dataset×seed cases.
- Cora: 32.7% nodes, Accuracy .630 vs full .798.
- Citeseer: 42.2% nodes, Accuracy .680 vs full .657.
- PubMed: 43.2% nodes, Accuracy .768 vs full .780.
- GBGC preprocessing is much slower than heavy-edge and the public artifact has
  no executable code. Nevertheless, the assumed “existing granular method is
  off frontier” premise is false. GNN-3, heterophily and scaling are stopped.

# Semantic Codebook

Not run. This line has no empirical signal and high collision with task-aware
quantization/rate-distortion/progressive communication.

# Failed ideas

- Validation marginal-value F5: does not close FED oracle gap or beat simple
  allocations at equal communication.
- Nonuniform GNN cut: not implemented because adaptive GBGC is already on the
  empirical node-risk frontier.
- Standalone Theory theorem: downgraded because current optimization is a
  pruning/model-selection policy-class expansion.
- Author-code GBGC reproduction: impossible; public repository contains only an
  appendix PDF and no license/code. Clean-room results are explicitly labeled.
- Original Citeseer run: invalid in-place reorder; all records retained and
  corrected with immutable rerun IDs.
- Semantic granular codebook: stopped before implementation due missing
  mechanism gap.

# Current P0/P1/Rejected

## P0

None.

## P1

1. **Heterogeneous global-threshold Pareto regret** — stable empirical signal,
   but known-region routing and pruning/SRM collisions prevent P0.
2. **Communication-budgeted client granularity allocation problem** — Digits has
   a stable uniform→oracle gap, but the estimated allocator is rejected.

## Rejected

- GNN nonuniform allocation prototype.
- Hierarchical granular semantic codebook for this round.
- FED F5 validation marginal-value mechanism.
- Standalone generic risk-budget tree-pruning theory claim.

# Most important unexpected finding

The allocation **problem** is stronger than the allocation **mechanism**:
Uniform→Oracle gaps are stable in Theory and FED, while the simple estimated
allocator fails; in GNN the closest existing adaptive granular method already
occupies the frontier, so no allocation problem remains there.

# Next decisive kill test

The cheapest decisive test is the FED marginal-value prediction audit on the
existing 60 Digits settings: compute per-client validation/test marginal-value
rank correlation under leave-client-out/seed evaluation. If median |rho| < 0.3,
reject validation risk-value allocation and keep FED only as a negative/problem
paper. No new large dataset should be run before this result.

# Line scores

| Line | N | Signal | Value | Depth | Theory | Compute | Repro | Collision | Score | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Theory | 2 | 5 | 2 | 3 | 3 | 4 | 5 | 5 | 23 | P1 application explanation |
| Federated | 3 | 3 | 5 | 2 | 2 | 5 | 5 | 4 | 28 | P1 problem; F5 rejected |
| GNN | 1 | 1 | 4 | 1 | 1 | 4 | 4 | 5 | 12 | Reject |
| Semantic codebook | 2 | 0 | 3 | 0 | 1 | 5 | 1 | 4 | 9 | Reject/not run |

Score uses the requested formula. A higher FED score does not override its kill
gate: empirical mechanism performance is negative and only one dataset was run.
