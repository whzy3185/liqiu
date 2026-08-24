# V2 theory collision audit

## Claim

Determine whether global-purity Pareto regret and risk-budget tree cuts are more
than existing tree pruning/model-selection theory expressed with granular-ball
vocabulary.

## Evidence

The implemented G3 problem fixes a maximal binary partition tree and selects a
cut by validation risk under leaf-count constraints. The oracle permits
region-specific cuts. This is mathematically close to:

- CART/cost-complexity and optimal tree pruning;
- validation-selected structural risk minimization;
- adaptive partition/histogram classifiers;
- classification-aware quantization and task-aware rate-distortion;
- generic constrained representation/model selection.

Adjacent records include cost-complexity pruning of ensembles
(10.1007/PL00011678), small-sample tree pruning
(10.1016/B978-1-55860-335-6.50048-9), Rademacher/SRM penalties
(10.1109/18.930926), classification-aware quantization
(10.1007/978-3-031-06947-5_5), and model-aware task-oriented rate-distortion
(10.1109/ICIP61757.2026.11630445).

## Negative evidence

Current positive results use known heterogeneous region routing and a test oracle.
The fact that a restricted global-threshold family has regret relative to a
larger nonuniform-cut family is a general policy-class inclusion phenomenon.
No granular-ball-specific recursive geometry lower bound has been proved.

## Closest literature

In addition to generic pruning/partition theory, 2026 MDL-GBC already performs
local model selection among retain/split/core-boundary granular explanations
(arXiv:2605.11406). That is a direct local-granulation mechanism collision.

## Collision risk

HIGH for standalone theory; MEDIUM for a GBC-specific empirical/theoretical
explanation attached to an application with a new resource metric.

## Decision

`P1_APPLICATION_EXPLANATION`. The Theory-3 empirical signal is retained, but the
current cut optimization is not a standalone novel theorem. P0 requires a
granular-specific lower bound or an application mechanism not reducible to
ordinary pruning/model selection.

## Next kill test

Use the same frontier language in GNN coarsening. If risk-budget nonuniform cuts
do not outperform strong graph coarsening at fixed nodes/time/memory, stop the
cross-domain theory story.
