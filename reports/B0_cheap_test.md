# B0 Feature-Selection Membership Cheap Test

The official lianxiaoyu724 GBFRS selector and FRFS, Mutual Information, and
ReliefF were evaluated on Breast Cancer, Sonar, and Spambase. Every dataset used
three frozen seeds and 12 shadow releases per seed. Attack cross-validation was
grouped by shadow release, so no test fold saw the same feature-selection output
as its training folds.

GBFRS has no practically meaningful membership signal. Across its mask,
mask-plus-count, and partial-ranking releases and both attacks, mean ROC-AUC is
0.499. The dataset aggregates are 0.505 (Breast Cancer), 0.490 (Sonar), and
0.502 (Spambase). No GBFRS aggregate reaches the preregistered 0.60 threshold.

| method | mean ROC-AUC | mean selection Jaccard | mean selected count |
| --- | ---: | ---: | ---: |
| GBFRS | 0.499 | 0.207 | 2.07 |
| FRFS | 0.507 | 0.491 | 2.07 |
| Mutual Information | 0.504 | 0.270 | 2.07 |
| ReliefF | 0.504 | 0.457 | 2.07 |

GBFRS is less stable by this standard Jaccard statistic, but that instability
does not yield a membership attack signal. The complete per-release, per-seed
record is in `results/B0_cheap_raw.csv`; all shadow outputs are in
`results/B0_cheap_shadow_outputs.jsonl`.
