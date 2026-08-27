# Privacy-Refinement Experiment Budget

The host has 16 GB RAM, with an estimated 5.69 GB currently available and a
4 GB swap volume. The initial memory-safe budget is 4.28 GB:
`min(0.75 * available, 0.65 * total)`. CPU is an Apple M5 with 10 cores; CUDA
is unavailable, so the first stage is CPU-only.

## Initial A3 plan

- Six public numeric classification datasets.
- Five fixed seeds: 1, 7, 21, 42, 2026.
- Five predeclared refinement thresholds: 0.70, 0.80, 0.90, 0.95, 0.99.
- Three release levels and two attacks: logistic regression and random forest.
- Matched-k KMeans is mandatory for every GB trajectory point.
- Outer workers start at two with `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`.

The data choice is exploratory but rule-based: prioritize public numeric tasks
with enough rows for a holdout membership attack and plausible refinement
heterogeneity (nontrivial class overlap or moderate dimensionality). It is not
permitted to discard a dataset or seed after seeing leakage results.

## Adaptive escalation

A single medium dataset benchmark determines observed time and RSS. Initial
expansion prioritizes synthetic regime search, then extra seeds around any
discovered condition, then targeted real datasets. A larger generic benchmark
count is secondary. The same inclusion rule, controls, releases, and reporting
apply at every tier.

No GPU-only model or new granular-ball algorithm is introduced merely to use
hardware. Raw intermediate records are checkpointed after each unit of work.
