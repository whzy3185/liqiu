# Granular-ball core label-noise stress

## Decision

`P1` research status; `P0-strength` failure evidence. At fixed
`tau=.85`, both 20% and 30% label noise make every one of the 120 paired
family/noise-kind/generator/seed comparisons simultaneously fragment more
and lose clean-test accuracy. This clears the preregistered cross-family,
two-generator, five-seed evidence bar. It is not P0 because the mechanism and
novelty gates are unresolved; no repair mechanism is promoted.

The result is not merely that noisy labels hurt classifiers. Increasing the
purity demand consumes many more granular-balls while clean risk worsens, and
the useful purity region changes with the noise regime. That resource-risk
reversal is the GB-specific signal.

The 2026 collision gate is direct: CMGBIFSC
(10.1016/j.asoc.2026.116020) and ScOrGBC
(10.1016/j.asoc.2026.114852) explicitly address excessive fragmentation
caused by high purity, alongside occupied boundary-driven generation work.
The stable failure therefore supports replication/diagnosis, not a novelty
claim, until objective- and code-level separation is established.

## Frozen evidence

- Source: `experiments/results/experiments.jsonl` selected by the 240 config IDs in
  `experiments/configs/core_exploration/noise/`.
- Selected-row canonical SHA-256: `58e4a280e0b645669ff878c451db6d96aa1a310f89dbfa7faed242d4a69394a7`.
- Implementation commit recorded by every row: `66b1d387efcd8dc459d4d56ad923fcc5877f1e3f`.
- The frozen GB-core batch has 400 rows: 240 noise, 120 imbalance, and 40
  shift. This report analyzes the complete 240-row noise subset.
- Complete factorial: 3 families x 2 noise mechanisms x 4 rates x 2
  generators x 5 seeds = 240 successful runs.
- Each run contains `tau in {.60,.75,.85,.95,1.0}` plus RandomForest,
  RBF-SVM, and 5-NN trained on the same corrupted labels and evaluated on an
  independently generated clean test set. Features are unchanged by label
  corruption.

## Fixed-purity phase

All rows below use `tau=.85`; changes are paired against the matching
zero-noise family, noise-kind, generator, and seed.

| Noise rate | Clean-test Accuracy | Delta Accuracy (pp) | Granules | Delta granules | Fragmentation | Worse and more fragmented | Gap to best reference (pp) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 93.77% | -- | 47.73 | -- | 7.96% | -- | -1.38 |
| 0.1 | 90.03% | -3.74 | 66.45 | +18.72 | 11.07% | 56.67% | -3.69 |
| 0.2 | 78.71% | -15.06 | 128.10 | +80.37 | 21.35% | 100.00% | -7.60 |
| 0.3 | 69.04% | -24.73 | 170.57 | +122.83 | 28.43% | 100.00% | -11.04 |

At 30% noise the mean granule count rises from 47.73 to 170.57
(`+122.83`) while clean-test Accuracy falls by 24.73 pp. At 20% noise
the corresponding change is `+80.37` granules and `-15.06` pp. All 60
pairs at each of these two rates move in the wrong resource-risk
direction.

## Cross-family replication at 30% noise

| Family | Noise | Generator | Delta Accuracy (pp) | Delta granules | Seeds worse and more fragmented |
|---|---|---|---:|---:|---:|
| gaussian_blobs | symmetric | kmeans | -26.50 | +275.00 | 5/5 |
| gaussian_blobs | symmetric | class_means | -25.77 | +231.20 | 5/5 |
| gaussian_blobs | boundary | kmeans | -30.00 | +40.40 | 5/5 |
| gaussian_blobs | boundary | class_means | -31.73 | +24.00 | 5/5 |
| moons | symmetric | kmeans | -27.27 | +280.60 | 5/5 |
| moons | symmetric | class_means | -25.47 | +233.80 | 5/5 |
| moons | boundary | kmeans | -29.33 | +19.60 | 5/5 |
| moons | boundary | class_means | -29.38 | +15.20 | 5/5 |
| spirals | symmetric | kmeans | -18.22 | +152.20 | 5/5 |
| spirals | symmetric | class_means | -17.47 | +155.40 | 5/5 |
| spirals | boundary | kmeans | -17.60 | +24.60 | 5/5 |
| spirals | boundary | class_means | -18.00 | +22.00 | 5/5 |

Symmetric noise produces the largest ball explosion because random flips
are spatially scattered. Boundary noise still increases fragmentation in
every seed, including on the already highly fragmented spiral family.

## Strong point references

Reference rows are deduplicated across the two identical GB-generator
copies, leaving 15 independent family/seed results per noise-kind/rate.
Values are clean-test Accuracy.

| Noise | Rate | RandomForest | RBF-SVM | 5-NN |
|---|---:|---:|---:|---:|
| symmetric | 0.0 | 94.31% | 87.05% | 95.16% |
| symmetric | 0.1 | 92.74% | 85.66% | 93.86% |
| symmetric | 0.2 | 88.27% | 84.74% | 88.80% |
| symmetric | 0.3 | 78.74% | 84.26% | 79.28% |
| boundary | 0.0 | 94.31% | 87.05% | 95.16% |
| boundary | 0.1 | 86.66% | 85.98% | 87.18% |
| boundary | 0.2 | 77.14% | 73.06% | 77.56% |
| boundary | 0.3 | 67.86% | 63.99% | 68.66% |

At 30% symmetric noise, RBF-SVM is strongest on average (84.26%); at
30% boundary noise, 5-NN is strongest (68.66%). The fixed `tau=.85` GB
mean is 11.04 pp below the best reference selected within each run. The
references also degrade, so only the paired fragmentation-plus-risk
reversal is treated as the mechanism evidence.

## Purity sensitivity

The clean-oracle quantities below are diagnostics only; they may not be
used as a deployable selector.

| Noise rate | Mean Accuracy range across tau (pp) | Clean-oracle gain over tau=.85 (pp) | Mean max/min granules | tau=1 minus tau=.85 (pp) | Runs with >=1 pp oracle gain |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 12.78 | 0.43 | 5.27x | +0.28 | 16.67% |
| 0.1 | 13.17 | 1.19 | 39.16x | -4.39 | 40.00% |
| 0.2 | 14.43 | 9.01 | 52.61x | -1.67 | 68.33% |
| 0.3 | 16.36 | 14.04 | 45.46x | -0.87 | 85.00% |

A single global purity level is not robust over regimes. Across all 240
runs, `tau=.75` has the best average Accuracy among the five fixed choices
but still has 4.65 pp mean clean-oracle regret. At 30% noise, 85% of runs
could gain at least 1 pp by changing `tau`, while choosing that change
from clean test labels would leak the target.

## Limitations

- This is synthetic binary classification with 600 training and 1,200
  clean-test samples; it is a failure map, not a benchmark claim.
- The family generator is held fixed while labels change. This isolates
  purity chasing but does not cover feature noise, open-set noise, or
  annotator dependence.
- RF/RBF-SVM/5NN have their standard frozen settings, not noise-specific
  tuning. The comparison prevents a GB-only claim but does not exhaust
  robust-learning baselines.
- The best `tau` and best reference are clean-test oracles used only for
  diagnosis.

## Cheapest kill test

First compare the split/stop objectives of CMGBIFSC and ScOrGBC against
this failure map. **Reject C1** if either already penalizes the same
purity-driven fragmentation under noisy/boundary labels and exposes the
same clean-risk/resource reversal. Only if that equivalence test fails,
run one nested-selection batch at exactly 20% noise: 3 families x 2 noise
kinds x 2 GB generators x 5 seeds = 60 fits. Select `tau` from the frozen
five-value grid using only a held-out validation set with the same noisy
label process, then reveal the existing clean test once. **Reject C1 as
a research direction** if the selected point is within 1 pp of the
clean-oracle Accuracy in at least 80% of cells and its mean Accuracy is
within 1 pp of the best frozen RF/RBF-SVM/5NN reference without using more
granules than `tau=.85`. Otherwise retain P1 and next run the closest
licensed author baseline. Do not tune a new split rule
before this selector test.
