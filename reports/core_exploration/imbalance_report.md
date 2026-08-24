# Granular-ball core class-imbalance stress

## Decision

`REJECT` C2 as a standalone research direction. The frozen data show a
P0-strength failure at the preregistered `tau=.85`: every run at 20:1 and
50:1 stops at one majority ball and has zero minority recall. However, this
is not a hidden minority-only effect: balanced-test Accuracy also collapses
by 49.17 pp versus the 1:1 paired condition. The already-frozen `tau=1` arm
restores 92.91% mean minority recall at 50:1 with only 5.33 balls, so the
standalone failure is an obvious purity-stop mismatch, not evidence for a new
imbalanced granular-ball mechanism. Class-mapping and per-class allocation
repairs are also already occupied, so relabeling the threshold fix would not
clear novelty.

The useful residual is the conflict with the noise result: `tau=1` repairs
minority masking here but causes severe noise fragmentation. That joint
constraint belongs under C1/resource-aware stopping, not a separate C2 paper.

## Frozen evidence

- Source: `experiments/results/experiments.jsonl` selected by the 120 config IDs in
  `experiments/configs/core_exploration/imbalance/`.
- Selected-row canonical SHA-256: `b9d867f0e6180889b17acd37c5d6efe5d7fb9b0f0bdf8b98dde9f98502e32ab2`.
- Implementation commit recorded by every row: `66b1d387efcd8dc459d4d56ad923fcc5877f1e3f`.
- The frozen GB-core batch has 400 rows: 240 noise, 120 imbalance, and 40
  shift. This report analyzes the complete 120-row imbalance subset.
- Complete factorial: 3 families x 4 imbalance ratios x 2 generators x
  5 seeds = 120 successful runs.
- Training data are imbalanced; all tests are independently generated and
  balanced. Each run contains five purity thresholds and RF/RBF-SVM/5NN
  references trained on the same imbalanced sample.

## Minority masking at fixed purity

All GB rows below use `tau=.85`. The paired recall change is against the
matching 1:1 family, generator, and seed.

| Majority:minority | Accuracy | Macro-F1 | Minority recall | Granules | Fragmentation | Zero-recall runs | Paired recall change (pp) | Gap to best reference F1 (pp) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1:1 | 99.17% | 99.17% | 99.38% | 3.33 | 0.39% | 0.00% | -- | -0.64 |
| 5:1 | 96.39% | 96.36% | 93.06% | 3.33 | 0.50% | 0.00% | -6.32 | -3.36 |
| 20:1 | 50.00% | 33.33% | 0.00% | 1.00 | 0.16% | 100.00% | -99.38 | -65.50 |
| 50:1 | 50.00% | 33.33% | 0.00% | 1.00 | 0.17% | 100.00% | -99.38 | -64.20 |

At 20:1 and 50:1, the parent-ball majority fractions are approximately
95.19% and 98.01%. They already exceed `tau=.85`, so the tree does not
split. Relative to the paired 1:1 runs, the 50:1 condition loses 99.38 pp
minority recall, 65.83 pp Macro-F1, and 49.17 pp Accuracy while using
2.33 fewer balls. The resource improvement is therefore underfitting,
not an acceptable accuracy/resource trade.

## Cross-family replication at 50:1

| Family | Generator | Accuracy | Macro-F1 | Minority recall | Granules | Zero-recall seeds |
|---|---|---:|---:|---:|---:|---:|
| density_equal | kmeans | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |
| density_equal | class_means | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |
| density_shift | kmeans | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |
| density_shift | class_means | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |
| moons | kmeans | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |
| moons | class_means | 50.00% | 33.33% | 0.00% | 1.00 | 5/5 |

Both generators make the same constant-majority prediction in all 30
50:1 runs. This is cross-family replication of the stop-rule behavior,
but it does not distinguish a new generator mechanism.

## Strong point references

Reference rows are deduplicated across GB generator, leaving 15
family/seed results per ratio.

| Ratio | Reference | Accuracy | Macro-F1 | Minority recall |
|---:|---|---:|---:|---:|
| 1:1 | RandomForest | 99.65% | 99.65% | 99.76% |
| 1:1 | RBF-SVM | 99.76% | 99.76% | 99.77% |
| 1:1 | 5-NN | 99.80% | 99.80% | 99.87% |
| 5:1 | RandomForest | 99.09% | 99.09% | 98.42% |
| 5:1 | RBF-SVM | 99.57% | 99.57% | 99.27% |
| 5:1 | 5-NN | 99.69% | 99.69% | 99.50% |
| 20:1 | RandomForest | 96.24% | 96.20% | 92.66% |
| 20:1 | RBF-SVM | 98.38% | 98.37% | 96.82% |
| 20:1 | 5-NN | 98.59% | 98.59% | 97.22% |
| 50:1 | RandomForest | 94.79% | 94.66% | 89.64% |
| 50:1 | RBF-SVM | 97.52% | 97.50% | 95.06% |
| 50:1 | 5-NN | 94.49% | 94.33% | 89.00% |

At 50:1, RBF-SVM is the strongest reference (97.50% Macro-F1 and 95.06%
minority recall). RF and 5-NN retain 89.64% and 89.00% minority recall.
The `tau=.85` GB gap is therefore not caused by an information-free
training sample.

## Purity sensitivity and built-in kill test

| Ratio | tau=1 Accuracy | tau=1 Macro-F1 | tau=1 minority recall | Granules | Fragmentation | Gap to best reference F1 (pp) |
|---:|---:|---:|---:|---:|---:|---:|
| 1:1 | 99.63% | 99.63% | 99.55% | 17.60 | 1.58% | -0.18 |
| 5:1 | 99.59% | 99.59% | 99.31% | 10.37 | 1.48% | -0.13 |
| 20:1 | 98.51% | 98.50% | 97.16% | 8.27 | 1.32% | -0.33 |
| 50:1 | 96.41% | 96.36% | 92.91% | 5.33 | 0.88% | -1.17 |

For both 20:1 and 50:1, raising `tau` from `.85` to `1.0` changes the
model from one ball/zero recall to a small multi-ball model. At 20:1 it
reaches 98.50% Macro-F1, only 0.33 pp below the best per-run reference; at
50:1 it reaches 96.36%, 1.17 pp below. The frozen threshold sweep has
therefore already executed the cheapest standalone kill test, and it
kills C2 under the current noise-free design.

## Limitations

- Balanced tests intentionally expose minority masking; deployment-prior
  accuracy and cost-sensitive risk are not evaluated.
- The minority class remains represented in training, even at 50:1. This
  does not cover few-shot class absence or multiclass long tails.
- The two density families are easily separable. Moons carries most of
  the residual error, so the aggregate rescue must not be sold as a broad
  imbalanced-learning improvement.
- Model size is not comparable across GB granules and RF/SVM/5NN; only
  predictive metrics are compared to point references.

## Cheapest kill test

No additional standalone C2 run is justified: the frozen `tau=1` arm is
the cheapest kill test and passes the repair gate (greater than 90% mean
minority recall with less than 2% fragmentation at 50:1). Reopen only as
a joint noise-imbalance interaction: ratio 20:1 plus 20% symmetric label
noise, 3 families x 2 generators x 5 seeds = 30 runs on the same five
thresholds. **Reject the joint hypothesis** if one prespecified global
threshold is within 1 pp of the clean-test oracle Macro-F1 and within 20%
of its granule count in at least 80% of cells. Otherwise merge the signal
into C1's budgeted stopping problem; do not revive a standalone imbalance
candidate.
