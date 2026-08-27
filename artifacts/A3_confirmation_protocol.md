# Frozen A3 Conditional-Regime Confirmation

The discovery hypothesis is frozen as follows: in locally heterogeneous,
high-dimensional (`d >= 60`), low-redundancy (`<= 0.10`) mixtures with nonzero
label noise (`>= 0.05`), fine purity refinement (`>= 0.90`) produces higher
membership leakage from granular-ball summaries than matched-k KMeans releases.

Confirmation does not reuse discovery seeds. It uses seeds 2, 13, 73, 314, and
808 and four held-out nearby parameter points:

| dimension | redundant fraction | label noise |
| ---: | ---: | ---: |
| 60 | 0.0 | 0.05 |
| 60 | 0.1 | 0.15 |
| 100 | 0.0 | 0.05 |
| 100 | 0.1 | 0.15 |

All retain separation 2.0, density ratio 5.0, minority fraction 0.30, three
minority modes, 600 rows, the same releases/attacks, and matched-k KMeans.
Confirmation succeeds only if the GB-minus-KMeans contrast is materially
positive (at least +0.05) on average at fine refinement and is directionally
consistent across seeds and both attacks. No confirmation condition will be
changed after results are seen.
